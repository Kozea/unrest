class Framework(object):
    """
    UnRest Framework abstract class.

    Framework are instanciated with an `app` object which should be
    your framework instance and the `url` of this UnRest instance.

    You must implement the `register_route` method if you want to
    implement you own framework.

    # Arguments
        app: Your framework instance used in `register_route` to register
            route.
        url: The current UnRest url ('/api' by default)
    """

    def __init__(self, app, url):
        self.app = app
        self.url = url

    def register_route(self, path, method, parameters, function):
        """
        This method is called by your rest endpoints for each `path` and
        each `method` that should respond with the `function`.
        The route should allow optionally the `parameters` within the
        url. These parameters represent the primary keys.

        # Arguments
            path: The url of the endoint without arguments. ('/api/person')
            method: The HTTP method to register the route on.
            parameters: The primary keys of the model that can be given
                after the path. `PrimaryKey('id'), PrimaryKey('type')) -> \
'/api/person/<id>/<type>'`
            function: The route function
        """
        raise NotImplementedError(
            'You have to implement the register route method'
        )

    @property
    def external_url(self):
        """
        A property returning the external api url root.
        (Used in OPTIONS and openapi genration)
        """
        return self.url

    def _name(self, name):
        """
        This helper generates a unique name for endpoint {name}
        that you can use in your implementation.
        """
        return f"unrest__{self.url.lstrip('/').replace('/', '_')}__{name}"
