"""操作日志中间件"""
from .models import OperationLog

# 注意这里将参数名统一为了 detail 和 ip_address，匹配各个视图传来的参数
def log_operation(user, action, module, detail='', ip_address=''):
    """记录操作日志，并自动维持数量上限"""

    # 1. 修复字段名：使用 detail 而不是 content，并补全必填的 username
    OperationLog.objects.create(
        user=user if user and user.is_authenticated else None,
        username=user.username if user and user.is_authenticated else '匿名',
        action=action,
        module=module,
        detail=detail,  # 🚨 修复这里：对应模型中的 detail 字段
        ip_address=ip_address or None
    )

    # 2. 日志自动清理机制（维持 3000 条上限）
    LOG_LIMIT = 3000

    if OperationLog.objects.count() > LOG_LIMIT:
        boundary_log = OperationLog.objects.order_by('-created_at')[LOG_LIMIT - 1:LOG_LIMIT].first()

        if boundary_log:
            OperationLog.objects.filter(created_at__lt=boundary_log.created_at).delete()