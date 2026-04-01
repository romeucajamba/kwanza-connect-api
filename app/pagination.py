from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """Paginação padronizada com envelope de resposta consistente."""
    page_size            = 20
    page_size_query_param = 'page_size'
    max_page_size        = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'status':  200,
            'message': 'Lista obtida com sucesso.',
            'pagination': {
                'total':    self.page.paginator.count,
                'pages':    self.page.paginator.num_pages,
                'current':  self.page.number,
                'next':     self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'data': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'success':    {'type': 'boolean'},
                'status':     {'type': 'integer'},
                'message':    {'type': 'string'},
                'pagination': {
                    'type': 'object',
                    'properties': {
                        'total':    {'type': 'integer'},
                        'pages':    {'type': 'integer'},
                        'current':  {'type': 'integer'},
                        'next':     {'type': 'string', 'nullable': True},
                        'previous': {'type': 'string', 'nullable': True},
                    },
                },
                'data': schema,
            },
        }
