import logging
from functools import wraps

from flask import request as flask_request
from flask import url_for

from ..util import Request

log = logging.getLogger('unrest.flask')


class FlaskUnRest(object):
    """
    Unrest flask framework implementation.
    This is the framework abstraction you can implement for your own framework

    """

    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix

    def register_route(self, path, method, parameters, fun):
        """
        Register the given function for `path` and `method` with and without
        `parameters`.

        # Arguments
            path: The url of the endoint without arguments. ('/api/person')
            method: The HTTP method to register the route on.
            parameters: The primary keys of the model that can be given
                after the path. `PrimaryKey('id'), PrimaryKey('type')) -> \
'/api/person/<id>/<type>'`
            fun: The route function
        """
        name = self._name(fun.__name__)
        getattr(fun, '__func__', fun).provide_automatic_options = False

        @wraps(fun)
        def unrest_fun(**url_parameters):
            request = Request(
                flask_request.url,
                flask_request.method,
                url_parameters,
                flask_request.args,
                flask_request.data,
                flask_request.headers,
            )

            response = fun(request)

            return self.app.response_class(
                response.payload,
                status=response.status,
                headers=response.headers,
            )

        if self.app.view_functions.pop(name, None):
            log.info('Overriding route %s' % name)

        self.app.add_url_rule(path, name, unrest_fun, methods=[method])
        if parameters:
            path_with_params = (
                path + '/' + '/'.join('<%s>' % param for param in parameters)
            )

            log.info(
                'Registering route %s for %s for %s'
                % (name, path_with_params, method)
            )
            self.app.add_url_rule(
                path_with_params, name, unrest_fun, methods=[method]
            )
        else:
            log.info(
                'Registering route %s for %s for %s' % (name, path, method)
            )

    @property
    def url(self):
        """
        Return the api url root
        """
        return url_for(self._name('index'), _external=True)

    def _name(self, name):
        """Generate a unique name for endpoint"""
        return 'unrest__%s__%s' % (self.prefix, name)
