# pagination.py
from rest_framework.pagination import PageNumberPagination

class OptimizedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10
    django_paginator_class = 'django.core.paginator.Paginator'