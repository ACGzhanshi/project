"""用户序列化器"""
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'role_display', 'phone',
                  'province', 'score', 'subject_type', 'subjects',
                  'avatar', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at']

# ----- 管理员修改/添加用户时的手机号查重 -----
    def validate_phone(self, value):
        if value:
            qs = User.objects.filter(phone=value)
            # 如果是更新操作，排除当前用户自身
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError('该手机号已被其他用户绑定')
        return value

    # ----- 管理员修改/添加用户时的用户名查重 -----
    def validate_username(self, value):
        qs = User.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError('该用户名已存在，请更换')
        return value

class RegisterSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'role',
                  'phone', 'province']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError('两次密码不一致')
        return attrs

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('该手机号已被注册')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('该用户名已存在')
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField()


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""
    class Meta:
        model = User
        fields = ['phone', 'province', 'score', 'subject_type',
                  'subjects', 'avatar', 'is_active']
