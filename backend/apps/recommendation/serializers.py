"""推荐模块序列化器"""
from rest_framework import serializers
from .models import RecommendRecord, AssessmentQuestion, AssessmentResult


class RecommendRecordSerializer(serializers.ModelSerializer):
    """推荐记录序列化器"""
    university_name = serializers.CharField(source='university.name', read_only=True)
    major_name = serializers.CharField(source='major.name', read_only=True, default='')
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = RecommendRecord
        fields = '__all__'


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    """测评题目序列化器"""
    class Meta:
        model = AssessmentQuestion
        fields = '__all__'


class AssessmentResultSerializer(serializers.ModelSerializer):
    """测评结果序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AssessmentResult
        fields = '__all__'


class RecommendInputSerializer(serializers.Serializer):
    """推荐输入序列化器"""
    score = serializers.IntegerField(min_value=0, max_value=750)
    province = serializers.CharField(max_length=20)
    subject_type = serializers.CharField(max_length=10)
    subjects = serializers.CharField(max_length=100, required=False, default='')
    interest_majors = serializers.CharField(max_length=200, required=False, default='')
