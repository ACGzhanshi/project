"""志愿填报序列化器"""
from rest_framework import serializers
from .models import VolunteerForm, VolunteerItem


class VolunteerItemSerializer(serializers.ModelSerializer):
    """志愿项序列化器"""
    university_name = serializers.CharField(source='university.name', read_only=True)
    major_name = serializers.CharField(source='major.name', read_only=True, default='')

    class Meta:
        model = VolunteerItem
        fields = '__all__'


class VolunteerFormSerializer(serializers.ModelSerializer):
    """志愿表序列化器"""
    items = VolunteerItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = VolunteerForm
        fields = '__all__'


class VolunteerFormCreateSerializer(serializers.ModelSerializer):
    """志愿表创建序列化器"""
    items = serializers.ListField(child=serializers.DictField(), write_only=True, required=False, default=[])

    class Meta:
        model = VolunteerForm
        fields = ['name', 'score', 'province', 'subject_type', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        form = VolunteerForm.objects.create(**validated_data)
        for item_data in items_data:
            VolunteerItem.objects.create(form=form, **item_data)
        return form
