class Idiom(object):
    """
    UnRest Idiom abstract class.

    Idioms are a way to alter how UnRest speaks with the rest of the world.
    The default implementation #::unrest.idiom.unrest#UnRestIdiom+1 parses json
    from request and generates json from response.

    To implement an idiom you have to implement the `request_to_payload` and
    the `data_to_response` methods described below.

    You can also override the `alter_query` method to add functionality to the
    idiom based on the `request`.
    (i.e. implementing sort / filter query parameters)

    # Arguments
        rest: The current rest instance
    """

    def __init__(self, rest):
        self.rest = rest

    def request_to_payload(self, request):
        """
        This method takes a #::unrest.util#Request `request` parameter and
        returns a payload dict.

        # Arguments
            request: The #::unrest.util#Request request

        # Returns
        A dict containing the request payload data.
        """
        raise NotImplementedError()

    def data_to_response(self, data, request, status=200):
        """
        This method takes a data dict returned by the route and return
        a #::unrest.util#Response object.


        # Arguments
            data: The data dict returned by the route
            request: The original #::unrest.util#Request request
            status: The current status (500 if route raised an error)

        # Returns
        An #::unrest.util#Response response object.
        """
        raise NotImplementedError()

    def alter_query(self, request, query):
        """
        This method takes the `request` and the current `query` and returns
        a modified `query` from the `request`.

        # Arguments
            data: The data dict returned by the route
            request: The original #::unrest.util#Request request
            status: The current status (500 if route raised an error)

        # Returns
        The modified `query`.
        """
        return query
