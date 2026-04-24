"""
推荐模块视图 - 已切换为协同过滤（CF）引擎
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .engine import generic_qianwen_chat
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import RecommendRecord, AssessmentQuestion, AssessmentResult
from .serializers import (
    RecommendRecordSerializer, AssessmentQuestionSerializer,
    AssessmentResultSerializer, RecommendInputSerializer
)
# 引入 CF 算法逻辑
from .cf_model import get_cf_recommendations, train_cf_model
from .engine import get_recommendations, qianwen_analyze
from apps.universities.models import University, Major, AdmissionScore
from apps.system.middleware import log_operation

class RecommendViewSet(viewsets.GenericViewSet):
    """智能推荐接口"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def ai_analyze(self, request):
        """千问AI智能分析（已打通测评结果）"""
        score = request.data.get('score')
        province = request.data.get('province')
        recommendations = request.data.get('recommendations', {})

        # ----- 新增逻辑：去数据库查询该用户最新的测评记录 -----
        assessment_data = None
        latest_assessment = AssessmentResult.objects.filter(
            user=request.user
        ).order_by('-created_at').first()

        if latest_assessment:
            # 提取最高分的维度
            dimensions = latest_assessment.result
            top_dim = '综合类'
            if isinstance(dimensions, dict) and dimensions:
                top_dim = max(dimensions, key=dimensions.get)

            assessment_data = {
                'top_dimension': top_dim,
                'recommended_majors': latest_assessment.recommended_majors
            }
        # -----------------------------------------------------

        # 将 assessment_data 传给 engine 里的千问函数
        analysis = qianwen_analyze(score, province, recommendations, assessment_data=assessment_data)

        return Response({'code': 200, 'data': {'analysis': analysis}})

    @action(detail=False, methods=['post'])
    def smart_match(self, request):
        """智能匹配推荐 (基于分数线统计)"""
        serializer = RecommendInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            recommendations = get_recommendations(
                score=data['score'],
                province=data['province'],
                subject_type=data['subject_type'],
                subjects=data.get('subjects', ''),
                interest_majors=data.get('interest_majors', '')
            )
        except ValueError as e:
            # 捕获到“没有数据”等业务逻辑错误，返回 400 给前端弹窗提示
            return Response({'code': 400, 'message': str(e)}, status=400)

        recommendations = get_recommendations(
            score=data['score'],
            province=data['province'],
            subject_type=data['subject_type'],
            subjects=data.get('subjects', ''),
            interest_majors=data.get('interest_majors', '')
        )

        # 记录推荐历史
        for level, items in recommendations.items():
            for item in items:
                RecommendRecord.objects.create(
                    user=request.user,
                    university_id=item['university_id'],
                    level=level,
                    score=data['score'],
                    probability=item['probability'],
                    reason=f"基于历年录取数据智能推荐"
                )

        log_operation(request.user, '智能推荐', '推荐系统',
                      f'执行智能匹配推荐，分数{data["score"]}，{data["province"]}',
                      request.META.get('REMOTE_ADDR', ''))

        return Response({
            'code': 200,
            'data': recommendations
        })



    @action(detail=False, methods=['get'])
    def history(self, request):
        """推荐历史"""
        records = RecommendRecord.objects.filter(
            user=request.user
        ).order_by('-created_at')
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = RecommendRecordSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RecommendRecordSerializer(records, many=True)
        return Response({'code': 200, 'data': serializer.data})


class AssessmentQuestionViewSet(viewsets.ModelViewSet):
    """专业测评题库管理接口"""
    queryset = AssessmentQuestion.objects.all().order_by('order')
    serializer_class = AssessmentQuestionSerializer

    # 允许搜索题目内容和按维度过滤
    filterset_fields = ['category']
    search_fields = ['content']

class AssessmentViewSet(viewsets.GenericViewSet):
    """专业测评接口 - 已集成协同过滤推荐"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def questions(self, request):
        """获取测评题目"""
        questions = AssessmentQuestion.objects.all().order_by('order')
        serializer = AssessmentQuestionSerializer(questions, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(detail=False, methods=['post'])
    def submit(self, request):
        """提交测评并执行 CF 推荐"""
        answers = request.data.get('answers', {})
        if not answers:
            return Response({'code': 400, 'message': '请完成测评'}, status=400)

        # 1. 计算各维度得分
        dimensions = {}
        for q_id, answer in answers.items():
            try:
                question = AssessmentQuestion.objects.get(id=q_id)
                cat = question.category
                # 计分逻辑：A=1, B=2, C=3, D=4
                dimensions[cat] = dimensions.get(cat, 0) + ord(answer) - ord('A') + 1
            except AssessmentQuestion.DoesNotExist:
                continue

        if not dimensions:
            return Response({'code': 400, 'message': '无效的测评数据'}, status=400)

        # 2. 确定“种子专业”以驱动 CF 算法
        # 找出得分最高的维度，并根据该维度选择一个代表性专业ID（种子）
        max_dim = max(dimensions, key=dimensions.get)

        # 种子映射（仅用于在CF矩阵中定位相似群体）
        seed_map = {
            '逻辑思维': 1,  # 假设 1 是计算机科学
            '语言表达': 11, # 假设 11 是法学
            '艺术创造': 15, # 假设 15 是视觉传达
            '社会服务': 21, # 假设 21 是临床医学
            '商业管理': 25, # 假设 25 是金融学
            '自然探索': 30, # 假设 30 是生物技术
        }
        seed_major_id = seed_map.get(max_dim, 1)

        # 3. 调用协同过滤算法获取相似专业
        # 该算法会基于 item_similarity_df 找出与种子专业最相关的其他专业
        cf_results = get_cf_recommendations(seed_major_id, top_n=10)
        recommended_major_ids = [item['major_id'] for item in cf_results]

        # 4. 从数据库获取完整的专业信息
        matched_majors = Major.objects.filter(
            id__in=recommended_major_ids
        ).select_related('university').order_by('-employment_rate')

        matched_list = []
        for m in matched_majors:
            matched_list.append({
                'university_id': m.university.id,
                'university_name': m.university.name,
                'university_province': m.university.province,
                'is_985': m.university.is_985,
                'is_211': m.university.is_211,
                'major_id': m.id,
                'major_name': m.name,
                'major_category': m.category,
                'employment_rate': float(m.employment_rate) if m.employment_rate else None,
                'avg_salary': m.avg_salary,
            })

        # 5. 保存结果
        recommended_names = "、".join([m.name for m in matched_majors[:3]])
        result = AssessmentResult.objects.create(
            user=request.user,
            answers=answers,
            result=dimensions,
            recommended_majors=f"协同过滤推荐：{recommended_names}"
        )

        return Response({
            'code': 200,
            'data': {
                'dimensions': dimensions,
                'recommended_majors': f"基于CF算法为您推荐：{recommended_names}",
                'top_dimension': max_dim,
                'matched_items': matched_list,
            }
        })

    @action(detail=False, methods=['post'])
    def train(self, request):
        """手动触发模型重训 (管理员接口)"""
        if request.user.role != 'sys_admin':
            return Response({'code': 403, 'message': '无权操作'}, status=403)

        try:
            train_cf_model()
            return Response({'code': 200, 'message': '协同过滤相似度矩阵更新成功'})
        except Exception as e:
            return Response({'code': 500, 'message': str(e)})

    @action(detail=False, methods=['get'])
    def my_results(self, request):
        """我的测评结果"""
        results = AssessmentResult.objects.filter(
            user=request.user
        ).order_by('-created_at')
        serializer = AssessmentResultSerializer(results, many=True)
        return Response({'code': 200, 'data': serializer.data})


@api_view(['POST'])
@permission_classes([AllowAny])
def ai_chat(request):
    """处理前端的 AI 聊天请求"""
    message = request.data.get('message')
    context = request.data.get('context', '')

    if not message:
        return Response({'code': 400, 'message': '请输入您的问题'}, status=400)

    reply = generic_qianwen_chat(message, context)
    return Response({'code': 200, 'data': {'reply': reply}})