import logging
from functools import wraps

from sanic import response

from ..util import Request
from . import Framework

log = logging.getLogger(__name__)


class SanicFramework(Framework):
    """
    Unrest #::unrest.framework#Framework implementation for Sanic.
    Sadly only synchroneous sqlalchemy query are supported for now.

    Requires [Sanic](https://sanicframework.org/) to be installed.
    """

    def register_route(self, path, method, parameters, function):
        name = self._name(function.__name__)

        @wraps(function)
        def unrest_fun(request, **url_parameters):
            req = Request(
                request.url,
                request.method,
                url_parameters,
                dict(request.args),
                request.body,
                request.headers,
            )

            res = function(req)

            return response.raw(
                res.payload.encode('utf-8'),
                status=res.status,
                headers=res.headers,
            )

        self.app.add_route(unrest_fun, path, methods=[method], name=name)
        if parameters:
            params = '/'.join(f'<{param}>' for param in parameters)
            path_with_params = f'{path}/{params}'
            log.info(
                f'Registering route {name} for {path_with_params} for {method}'
            )
            self.app.add_route(
                unrest_fun, path_with_params, methods=[method], name=name
            )
        else:
            log.info(f'Registering route {name} for {path} for {method}')

    @property
    def external_url(self):
        return self.app.url_for(
            self._name('index'), _external=self.app.config.get('SERVER_NAME')
        )
