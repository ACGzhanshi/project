"""院校序列化器"""
from rest_framework import serializers
from .models import University, Major, AdmissionScore, EnrollmentPlan

class UniversitySerializer(serializers.ModelSerializer):
    """院校信息序列化器"""
    class Meta:
        model = University
        fields = '__all__'

class MajorSerializer(serializers.ModelSerializer):
    """专业序列化器"""
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = Major
        # 使用 __all__ 会自动包含模型中的 discipline_eval 字段
        fields = '__all__'


class AdmissionScoreSerializer(serializers.ModelSerializer):
    """录取分数线序列化器"""
    university_name = serializers.CharField(source='university.name', read_only=True)
    major_name = serializers.CharField(source='major.name', read_only=True, default='')

    # 🚀 声明自定义关联字段：获取该分数线对应专业的学科评估结果
    major_discipline_eval = serializers.CharField(source='major.discipline_eval', read_only=True, default='')

    class Meta:
        model = AdmissionScore
        # 🚨 核心修复：不能只写 __all__，必须显式包含 major_discipline_eval
        fields = '__all__'

class EnrollmentPlanSerializer(serializers.ModelSerializer):
    """招生计划序列化器"""
    university_name = serializers.CharField(source='university.name', read_only=True)
    major_name = serializers.CharField(source='major.name', read_only=True, default='')

    class Meta:
        model = EnrollmentPlan
        fields = '__all__'


class UniversityListSerializer(serializers.ModelSerializer):
    """院校列表序列化器"""
    class Meta:
        model = University
        fields = ['id', 'name', 'code', 'province', 'city', 'level',
                  'type', 'is_985', 'is_211', 'is_double_first',
                  'ranking', 'employment_rate', 'logo']


class UniversityDetailSerializer(serializers.ModelSerializer):
    """院校详情序列化器"""
    majors = MajorSerializer(many=True, read_only=True)
    recent_scores = serializers.SerializerMethodField()

    class Meta:
        model = University
        fields = '__all__'

    def get_recent_scores(self, obj):
        # 这里的返回会调用上面的 AdmissionScoreSerializer，由于上面已修复，此处不会再报错
        scores = obj.scores.order_by('-year')[:30]
        return AdmissionScoreSerializer(scores, many=True).data