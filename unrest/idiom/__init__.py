class Idiom(object):
    def __init__(self, rest):
        self.rest = rest

    def request_to_payload(self, request):
        raise NotImplementedError()

    def data_to_response(self, data, request, status=200):
        raise NotImplementedError()

    def alter_query(self, request, query):
        return query
