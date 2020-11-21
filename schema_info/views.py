from django.shortcuts import render
from schema_info.models import MySQLSchema
from rest_framework import status, viewsets
from schema_info.serializers import MySQLSchemaSerializer, MySQLSchemaNameSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
import MySQLdb
from django.http import Http404


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page_num'
    max_page_size = 500


class SchemaViewSet(viewsets.ModelViewSet):
    queryset = MySQLSchema.objects.all()
    serializer_class = MySQLSchemaSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['status', 'schema', 'host_ip', 'port']

    @action(detail=False, methods=['get'])
    def get_distinct_schema_names(self, request, *args, **kwargs):
        queryset = self.get_queryset().values('schema').distinct()
        # 我们这里没有使用序列化器，而是将query set变成了一个列表返回
        name_list = [d["schema"] for d in list(queryset)]
        return Response(name_list)

    @action(detail=True, methods=['get'])
    def get_process_list(self, request, pk=None, *args, **kwargs):
        if pk is None:
            raise Http404
        instance = self.get_queryset().get(pk=pk)
        db = MySQLdb.connect(host=instance.host_ip, port=instance.port, user="root",
                            passwd="afTD]$]yQ@2:{LQSEQ6bt$]F1mK}Kt#1", db=instance.schema)
        c = db.cursor()
        c.execute("show processlist;")
        results = c.fetchall()
        columns = ["id", "user", "host", "db", "command", "time", "state", "info"]

        process_lists = []
        for row in results:
            d = {}
            for idx, col_name in enumerate(columns):
                d[col_name] = row[idx]
            process_lists.append(d)
        return Response(process_lists)

    @action(detail=True, methods=['delete'], url_path="kill_process_list/<int:process_id>/")
    def kill_process_list(self, request, pk=None, process_id=None, *args, **kwargs):
        if pk is None or process_id is None:
            raise Http404
        instance = self.get_queryset().get(pk=pk)
        print("process_id", process_id)
        return Response("success")
