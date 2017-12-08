import logging

from flask import current_app, jsonify, request, url_for

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

        if self.app.view_functions.pop(name, None):
            log.info('Overriding route %s' % name)
        getattr(fun, '__func__', fun).provide_automatic_options = False
        self.app.add_url_rule(path, name, fun, methods=[method])
        if parameters:
            log.info(
                'Registering route %s for %s for %s' % (name, path, method)
            )
            path_with_params = path + '/' + '/'.join(
                '<%s>' % param for param in parameters
            )

            log.info(
                'Registering route for %s for %s' % (path_with_params, method)
            )
            self.app.add_url_rule(
                path_with_params, name, fun, methods=[method]
            )

    def request_json(self):
        """
        Must return the string of the current JSON request content or None
        """
        if not request.is_json:
            return None

        return request.data.decode('utf-8')

    def send_json(self, json, status_code=200):
        """
        Send a `status_code` JSON response with `json` as content

        # Arguments
            json: The JSON string to send.
            status_code: The response status code. (Default: 200)
        """
        return current_app.response_class(
            (json, '\n'),
            status=status_code,
            mimetype=current_app.config['JSONIFY_MIMETYPE']
        )

    def send_error(self, message, status_code):
        """
        Send an error as a JSON response with the given status code.

        # Arguments
            message: The JSON string containing the error message.
            status_code: The HTTP status code (i.e. 402)
        """
        return jsonify(message), status_code

    @property
    def url(self):
        """
        Return the api url root
        """
        return url_for(self._name('index'), _external=True)

    def _name(self, name):
        """Generate a unique name for endpoint"""
        return 'unrest__%s__%s' % (self.prefix, name)
