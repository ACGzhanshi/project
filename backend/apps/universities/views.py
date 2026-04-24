"""院校视图"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Min, Max, Q
from .models import University, Major, AdmissionScore, EnrollmentPlan
from apps.system.middleware import log_operation
from .serializers import (
    UniversityListSerializer, UniversityDetailSerializer,UniversitySerializer,
    MajorSerializer, AdmissionScoreSerializer, EnrollmentPlanSerializer
)

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    仅系统管理员和数据管理员可写，其他用户仅可读
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ['sys_admin', 'data_admin']

class UniversityViewSet(viewsets.ModelViewSet):
    """院校管理接口"""
    queryset = University.objects.all().order_by('ranking')
    serializer_class = UniversitySerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = {
        'province': ['exact'],
        'level': ['exact'],
        'type': ['exact'],
        'is_985': ['exact'],
        'is_211': ['exact'],
        'is_double_first': ['exact']
    }
    search_fields = ['name', 'code', 'city']

    def get_client_ip(self):
        return self.request.META.get('REMOTE_ADDR', '')

    def perform_create(self, serializer):
        instance = serializer.save()
        log_operation(self.request.user, '新增', '院校管理', f'添加了院校: {instance.name}', self.get_client_ip())

    def perform_update(self, serializer):
        instance = serializer.save()
        log_operation(self.request.user, '修改', '院校管理', f'更新了院校信息: {instance.name}', self.get_client_ip())

    def perform_destroy(self, instance):
        name = instance.name
        instance.delete()
        log_operation(self.request.user, '删除', '院校管理', f'删除了院校: {name}', self.get_client_ip())

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UniversityDetailSerializer
        return UniversityListSerializer

    @action(detail=False, methods=['get'])
    def compare(self, request):
        """院校对比"""
        ids = request.query_params.get('ids', '').split(',')
        if len(ids) < 2:
            return Response({'code': 400, 'message': '至少选择两所院校'}, status=400)
        universities = University.objects.filter(id__in=ids)
        data = []
        for uni in universities:
            scores = uni.scores.filter(year__gte=2022).values('year').annotate(
                avg_min=Avg('min_score'), lowest=Min('min_score'), highest=Max('max_score')
            )
            data.append({
                'university': UniversityDetailSerializer(uni).data,
                'score_trend': list(scores)
            })
        return Response({'code': 200, 'data': data})

    @action(detail=True, methods=['get'], url_path='score_trends')
    def score_trends(self, request, pk=None):
        """获取某院校在特定省份的历年录取趋势（给ECharts画图用）"""
        # 【核心修复】：不要用 self.get_object()，绕过 province 过滤器的拦截
        try:
            uni = University.objects.get(pk=pk)
        except University.DoesNotExist:
            return Response({'code': 404, 'message': '院校不存在'}, status=404)

        # 如果前端没传省份，默认给个北京防止报错
        province = request.query_params.get('province', '北京')

        # 使用 annotate 去重，防止同一年有多个批次导致图表折线混乱
        scores = AdmissionScore.objects.filter(
            university=uni, province=province
        ).values('year').annotate(
            min_score=Min('min_score'),
            min_rank=Min('min_rank')
        ).order_by('year')

        years = [str(s['year']) for s in scores]
        min_scores = [s['min_score'] for s in scores]
        min_ranks = [s['min_rank'] for s in scores]

        return Response({
            'code': 200,
            'data': {
                'years': years,
                'min_scores': min_scores,
                'min_ranks': min_ranks
            }
        })

    @action(detail=False, methods=['get'])
    def provinces(self, request):
        """获取省份列表"""
        provinces = University.objects.values_list('province', flat=True).distinct()
        return Response({'code': 200, 'data': list(provinces)})


class MajorViewSet(viewsets.ModelViewSet):
    """专业管理接口"""
    queryset = Major.objects.all()
    serializer_class = MajorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['university', 'category', 'duration']
    search_fields = ['name', 'code']

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('no_page'):
            return None  # 返回 None 代表不分页，直接吐出所有数据
        return super().paginate_queryset(queryset)


class AdmissionScoreViewSet(viewsets.ModelViewSet):
    """录取分数线接口 (核爆兼容版)"""
    queryset = AdmissionScore.objects.all().order_by('-year')
    serializer_class = AdmissionScoreSerializer
    permission_classes = [IsAuthenticated]

    # 🚨 核心修复 1：把 province 和 subject_type 从死板的精确匹配过滤器中剔除！
    filterset_fields = ['university', 'year', 'batch']

    def get_queryset(self):
        queryset = super().get_queryset()

        # 截获前端传来的查询参数
        province = self.request.query_params.get('province')
        subject_type = self.request.query_params.get('subject_type')
        search = self.request.query_params.get('search')

        # 🚨 核心修复 2：移植智能推荐的模糊匹配逻辑
        if province:
            clean_province = province.replace('省', '').replace('市', '').replace('自治区', '').replace('壮族', '')
            queryset = queryset.filter(province__icontains=clean_province)

        if subject_type:
            subj_q = Q()
            if '理' in subject_type or '物' in subject_type:
                subj_q = Q(subject_type__icontains='理') | Q(subject_type__icontains='物') | Q(
                    subject_type__icontains='理工')
            elif '文' in subject_type or '史' in subject_type:
                subj_q = Q(subject_type__icontains='文') | Q(subject_type__icontains='史') | Q(
                    subject_type__icontains='文史')
            else:
                subj_q = Q(subject_type__icontains=subject_type)
            queryset = queryset.filter(subj_q)

        if search:
            # 🚨 核心修复 3：支持前端在下拉框旁边直接按“专业名称”模糊搜索
            queryset = queryset.filter(major__name__icontains=search)

        return queryset

    def get_client_ip(self):
        return self.request.META.get('REMOTE_ADDR', '')

    def perform_create(self, serializer):
        instance = serializer.save()
        log_operation(self.request.user, '新增', '专业管理',
                      f'为 [{instance.university.name}] 添加了专业: {instance.name}', self.get_client_ip())

    def perform_update(self, serializer):
        instance = serializer.save()
        log_operation(self.request.user, '修改', '专业管理', f'更新了专业信息: {instance.name}', self.get_client_ip())

    def perform_destroy(self, instance):
        name = instance.name
        univ_name = instance.university.name if instance.university else '未知院校'
        instance.delete()
        log_operation(self.request.user, '删除', '专业管理', f'删除了 [{univ_name}] 的专业: {name}',
                      self.get_client_ip())

    @action(detail=False, methods=['get'])
    def trend(self, request):
        """分数线趋势"""
        uni_id = request.query_params.get('university_id')
        province = request.query_params.get('province', '')
        if not uni_id:
            return Response({'code': 400, 'message': '请指定院校'}, status=400)
        scores = AdmissionScore.objects.filter(
            university_id=uni_id
        ).order_by('year')
        if province:
            scores = scores.filter(province=province)
        data = scores.values('year', 'subject_type').annotate(
            avg_min=Avg('min_score'), avg_avg=Avg('avg_score')
        )
        return Response({'code': 200, 'data': list(data)})


class EnrollmentPlanViewSet(viewsets.ModelViewSet):
    """招生计划接口"""
    queryset = EnrollmentPlan.objects.all().order_by('-year')
    serializer_class = EnrollmentPlanSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['university', 'year', 'province', 'subject_type']
