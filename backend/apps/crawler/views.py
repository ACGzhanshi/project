"""爬虫模块视图"""
import threading
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CrawlerTask, CrawlerData
from .serializers import CrawlerTaskSerializer, CrawlerDataSerializer
from .spider import crawl_universities, crawl_scores


class CrawlerTaskViewSet(viewsets.ModelViewSet):
    """爬虫任务管理"""
    queryset = CrawlerTask.objects.all().order_by('-created_at')
    serializer_class = CrawlerTaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task_type', 'status']

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """启动爬虫任务"""
        task = self.get_object()
        if task.status == 'running':
            return Response({'code': 400, 'message': '任务正在运行中'}, status=400)

        task.status = 'pending'
        task.save()

        crawl_func = {
            'university': crawl_universities,
            'score': crawl_scores,
            'major': crawl_universities,
            'plan': crawl_scores,
        }.get(task.task_type, crawl_universities)

        thread = threading.Thread(target=crawl_func, args=(task,))
        thread.daemon = True
        thread.start()

        from apps.system.middleware import log_operation
        log_operation(request.user, '启动爬虫', '数据采集', f'启动任务：{task.name}',
                      request.META.get('REMOTE_ADDR', ''))

        return Response({'code': 200, 'message': '任务已启动'})

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """停止爬虫任务"""
        task = self.get_object()
        if task.status != 'running':
            return Response({'code': 400, 'message': '任务未在运行中'}, status=400)

        task.status = 'failed'
        task.log += '\n任务被手动停止'
        task.save()

        from apps.system.middleware import log_operation
        log_operation(request.user, '停止爬虫', '数据采集', f'停止任务：{task.name}',
                      request.META.get('REMOTE_ADDR', ''))

        return Response({'code': 200, 'message': '任务已停止'})

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """查看任务日志"""
        task = self.get_object()
        return Response({'code': 200, 'data': {'log': task.log, 'status': task.status}})

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """查看爬取数据"""
        task = self.get_object()
        data_items = task.data_items.all()
        page = self.paginate_queryset(data_items)
        if page is not None:
            serializer = CrawlerDataSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CrawlerDataSerializer(data_items, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """爬虫统计"""
        from django.db.models import Sum, Count
        stats = CrawlerTask.objects.aggregate(
            total_tasks=Count('id'),
            total_data=Sum('success_count'),
        )
        type_stats = CrawlerTask.objects.values('task_type').annotate(
            count=Count('id'), data_count=Sum('success_count')
        )
        return Response({
            'code': 200,
            'data': {'overview': stats, 'by_type': list(type_stats)}
        })
