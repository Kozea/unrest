import logging

from flask import current_app, jsonify, request

log = logging.getLogger('unrest.flask')


class FlaskUnRest(object):
    """
    Unrest flask framework implementation.
    This is the framework abstraction you can implement for your own framework

    """
    def __init__(self, app):
        self.app = app

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
        if self.app.view_functions.pop(fun.__name__, None):
            log.info('Overriding route %s' % fun.__name__)
        getattr(fun, '__func__', fun).provide_automatic_options = False
        self.app.add_url_rule(
            path, fun.__name__, fun, methods=[method])
        if parameters:
            log.info('Registering route for %s for %s' % (path, method))
            path_with_params = path + '/' + '/'.join(
                '<%s>' % param for param in parameters)

            log.info('Registering route for %s for %s' % (
                path_with_params, method))
            self.app.add_url_rule(
                path_with_params, fun.__name__, fun, methods=[method])

    def request_json(self):
        """
        Must return the string of the current JSON request content or None
        """
        if not request.is_json:
            return None

        return request.data.decode('utf-8')

    def send_json(self, json):
        """
        Send a 200 JSON response with `json` as content

        # Arguments
            json: The JSON string to send.
        """
        return current_app.response_class(
            (json, '\n'),
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
