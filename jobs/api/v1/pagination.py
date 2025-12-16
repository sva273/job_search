from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination with 10 items per page"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_page_size(self, request):
        """Return page size, defaulting to 10"""
        if self.page_size_query_param:
            page_size = request.query_params.get(self.page_size_query_param)
            if page_size:
                try:
                    return min(int(page_size), self.max_page_size)
                except (KeyError, ValueError):
                    pass
        return 10
    
    def get_paginated_response(self, data):
        """Return a paginated style Response object"""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

