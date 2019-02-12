class Request(object):
    def __init__(self, url, method, parameters, query, payload, headers):
        self.url = url
        self.method = method
        self.parameters = parameters
        self.query = query
        self.payload = payload
        self.headers = headers


class Response(object):
    def __init__(self, payload, headers, status):
        self.payload = payload
        self.headers = headers
        self.status = status
