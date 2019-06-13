import logging
from functools import wraps

from flask import request as flask_request
from flask import url_for

from ..util import Request
from . import Framework

log = logging.getLogger(__name__)


class FlaskFramework(Framework):
    """
    Unrest #::unrest.framework#Framework implementation for Flask.

    Requires [flask](http://flask.pocoo.org/) to be installed.
    """

    def register_route(self, path, method, parameters, function):
        name = self._name(function.__name__)
        getattr(
            function, '__func__', function
        ).provide_automatic_options = False

        @wraps(function)
        def unrest_fun(**url_parameters):
            request = Request(
                flask_request.url,
                flask_request.method,
                url_parameters,
                dict(flask_request.args.lists()),
                flask_request.data,
                flask_request.headers,
            )

            response = function(request)

            return self.app.response_class(
                response.payload,
                status=response.status,
                headers=response.headers,
            )

        self.app.add_url_rule(path, name, unrest_fun, methods=[method])
        if parameters:
            params = '/'.join(f'<{param}>' for param in parameters)
            path_with_params = f'{path}/{params}'

            log.info(
                f'Registering route {name} for {path_with_params} for {method}'
            )
            self.app.add_url_rule(
                path_with_params, name, unrest_fun, methods=[method]
            )
        else:
            log.info(f'Registering route {name} for {path} for {method}')

    @property
    def external_url(self):
        return url_for(self._name('index'), _external=True)
