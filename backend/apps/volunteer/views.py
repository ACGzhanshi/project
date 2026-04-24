"""志愿填报视图"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import VolunteerForm, VolunteerItem
from .serializers import (
    VolunteerFormSerializer, VolunteerFormCreateSerializer,
    VolunteerItemSerializer
)
from apps.recommendation.engine import calculate_probability
from apps.universities.models import AdmissionScore
from django.db.models import Avg, Min, Q
import json

# 尝试导入测评结果模型
try:
    from apps.recommendation.models import AssessmentResult
except ImportError:
    AssessmentResult = None


class VolunteerFormViewSet(viewsets.ModelViewSet):
    """志愿表管理"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VolunteerForm.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return VolunteerFormCreateSerializer
        return VolunteerFormSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'code': 200,
            'message': '创建成功',
            'data': VolunteerFormSerializer(serializer.instance).data
        })

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """分析志愿表合理性 (增强排错版)"""
        form = self.get_object()
        items = form.items.all()
        if not items.exists():
            return Response({'code': 400, 'message': '志愿表为空'}, status=400)

        # 核心修复 1：严格去除省份首尾看不见的空格，防止匹配失败
        clean_province = form.province.replace('省', '').replace('市', '').replace('自治区', '').replace('壮族',
                                                                                                         '').strip()

        subj_q = Q()
        if '理' in form.subject_type or '物' in form.subject_type:
            subj_q = Q(subject_type__icontains='理') | Q(subject_type__icontains='物') | Q(
                subject_type__icontains='理工')
        elif '文' in form.subject_type or '史' in form.subject_type:
            subj_q = Q(subject_type__icontains='文') | Q(subject_type__icontains='史') | Q(
                subject_type__icontains='文史')
        else:
            subj_q = Q(subject_type__icontains=form.subject_type)

        analysis_items = []
        rush_count = stable_count = safe_count = 0

        for item in items:
            ref_score = None

            # 优先尝试获取【该专业】的真实分数线
            if item.major:
                major_score_data = AdmissionScore.objects.filter(
                    Q(province__icontains=clean_province),
                    subj_q,
                    university=item.university,
                    major=item.major,
                    year__gte=2022,
                    min_score__gt=0
                ).aggregate(avg=Avg('min_score'))

                if major_score_data['avg']:
                    ref_score = float(major_score_data['avg'])

            # 如果没选专业，或该专业在当地没数据，退回查【该院校】
            if not ref_score:
                uni_score_data = AdmissionScore.objects.filter(
                    Q(province__icontains=clean_province),
                    subj_q,
                    university=item.university,
                    year__gte=2022,
                    min_score__gt=0
                ).aggregate(avg=Avg('min_score'), abs_min=Min('min_score'))

                # 核心修复 2：防止类型导致 False，确保只要有数据就能算出分数
                if uni_score_data['avg'] is not None and uni_score_data['abs_min'] is not None:
                    ref_score = (float(uni_score_data['avg']) * 0.7) + (float(uni_score_data['abs_min']) * 0.3)
                elif uni_score_data['avg'] is not None:
                    ref_score = float(uni_score_data['avg'])

            if ref_score:
                # 确保传进去的 user_score 绝对是数字类型
                prob = calculate_probability(int(form.score), ref_score)
                item.probability = round(prob, 1)

                if prob < 45:
                    item.level = 'rush'
                    rush_count += 1
                elif prob < 80:
                    item.level = 'stable'
                    stable_count += 1
                else:
                    item.level = 'safe'
                    safe_count += 1
                item.save()

                analysis_items.append({
                    'order': item.order,
                    'university': item.university.name,
                    'major': item.major.name if item.major else '未定专业',
                    'probability': round(prob, 1),
                    'level': item.level
                })
            else:
                # 核心修复 3：真查不到数据时，赋值为 0，让前端渲染为“缺数据”
                item.probability = 0
                item.level = '未知'
                item.save()
                analysis_items.append({
                    'order': item.order,
                    'university': item.university.name,
                    'major': item.major.name if item.major else '未定专业',
                    'probability': 0,
                    'level': '缺数据'
                })

        total = len(items)
        suggestions = []
        if rush_count == 0:
            suggestions.append('建议增加1-2所冲刺院校，提升录取上限。')
        if safe_count == 0:
            suggestions.append('缺少保底院校，存在滑档风险，请务必增加保底志愿！')
        if rush_count > total * 0.5:
            suggestions.append('冲刺院校占比过高（>50%），建议适当增加稳妥和保底院校。')
        if stable_count >= total * 0.4 and safe_count >= 1:
            suggestions.append('志愿梯度合理，冲稳保搭配健康。')

        analysis = {
            'items': analysis_items,
            'summary': {
                'total': total,
                'rush': rush_count,
                'stable': stable_count,
                'safe': safe_count,
            },
            'suggestions': suggestions
        }

        import json
        form.analysis = json.dumps(analysis, ensure_ascii=False)
        form.status = 'analyzed'
        form.save()

        return Response({'code': 200, 'data': analysis})


    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """【修复】添加志愿项，支持接收专业ID"""
        form = self.get_object()

        # 复制数据以进行修改
        data = request.data.copy()
        data['form'] = form.id
        data['order'] = form.items.count() + 1

        # 兼容前端命名习惯（前端可能传 major_id 也可能传 major）
        if 'major_id' in data and not data.get('major'):
            data['major'] = data.pop('major_id')
        if 'university_id' in data and not data.get('university'):
            data['university'] = data.pop('university_id')

        serializer = VolunteerItemSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'code': 200, 'data': serializer.data})

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        """删除志愿项"""
        item_id = request.data.get('item_id')
        VolunteerItem.objects.filter(id=item_id, form_id=pk).delete()
        return Response({'code': 200, 'message': '删除成功'})