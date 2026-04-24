"""用户视图"""
from rest_framework import viewsets, status
from apps.system.middleware import log_operation
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    UserSerializer, RegisterSerializer,
    LoginSerializer, UserUpdateSerializer
)


class AuthViewSet(viewsets.GenericViewSet):
    """认证相关接口"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """用户注册"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'code': 200,
            'message': '注册成功',
            'data': UserSerializer(user).data
        })

    @action(detail=False, methods=['post'])
    def login(self, request):
        """用户登录"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if not user:
            return Response({
                'code': 401,
                'message': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({
                'code': 403,
                'message': '账号已被禁用'
            }, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)

        # 记录登录日志
        from apps.system.middleware import log_operation
        ip = request.META.get('REMOTE_ADDR', '')
        log_operation(user, '登录', '用户认证', f'用户{user.username}登录系统', ip)

        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def info(self, request):
        """获取当前用户信息"""
        return Response({
            'code': 200,
            'data': UserSerializer(request.user).data
        })

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """更新个人信息"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'code': 200,
            'message': '更新成功',
            'data': UserSerializer(request.user).data
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """修改密码"""
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not request.user.check_password(old_password):
            return Response({'code': 400, 'message': '原密码错误'}, status=400)
        request.user.set_password(new_password)
        request.user.save()
        return Response({'code': 200, 'message': '密码修改成功'})


class UserManageViewSet(viewsets.ModelViewSet):
    """用户管理接口（系统管理员）"""
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'phone']

    def get_client_ip(self):
        return self.request.META.get('REMOTE_ADDR', '')

    # --- 拦截新增 ---
    def perform_create(self, serializer):
        hashed_password = make_password('123456')
        user = serializer.save(password=hashed_password)
        log_operation(self.request.user, '新增', '用户管理', f'添加了新用户: {user.username}', self.get_client_ip())

    # --- 拦截修改 ---
    def perform_update(self, serializer):
        user = serializer.save()
        log_operation(self.request.user, '修改', '用户管理', f'更新了用户资料: {user.username}', self.get_client_ip())

    # --- 拦截删除 ---
    def perform_destroy(self, instance):
        username = instance.username
        instance.delete()
        log_operation(self.request.user, '删除', '用户管理', f'删除了用户: {username}', self.get_client_ip())

    def get_queryset(self):
        if self.request.user.role != 'sys_admin':
            return User.objects.none()
        return super().get_queryset()

    def perform_create(self, serializer):
        """管理员添加用户时，默认密码设为123456并加密"""
        hashed_password = make_password('123456')
        serializer.save(password=hashed_password)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """启用/禁用用户"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        action_name = '启用' if user.is_active else '禁用'
        log_operation(request.user, action_name, '用户管理', f'{action_name}了用户: {user.username}',
                      self.get_client_ip())
        return Response({
            'code': 200,
            'message': f"用户已{'启用' if user.is_active else '禁用'}"
        })

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """重置密码"""
        user = self.get_object()
        user.set_password('123456')
        user.save()
        log_operation(request.user, '重置密码', '用户管理', f'重置了用户 {user.username} 的密码', self.get_client_ip())
        return Response({'code': 200, 'message': '密码已重置为123456'})
