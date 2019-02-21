class Request(object):
    """
    The unrest request object created in the #::unrest.framework route wrapper.

    # Arguments
        url: The request url.
        method: The request method.
        parameters: The url parameters as dict.
        query: The query string parameters as dict.
        payload: The request body as bytes if any.
        headers: A mapping of request headers.
    """

    def __init__(self, url, method, parameters, query, payload, headers):
        self.url = url
        self.method = method
        self.parameters = parameters
        self.query = query
        self.payload = payload
        self.headers = headers


class Response(object):
    """
    The unrest response object created by the #::unrest.idiom.

    # Arguments
        payload: The response body as string.
        headers: A mapping of response headers.
        status: The response status code.
    """

    def __init__(self, payload, headers, status):
        self.payload = payload
        self.headers = headers
        self.status = status
