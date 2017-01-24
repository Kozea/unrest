import logging

from flask import current_app, jsonify, request

log = logging.getLogger('unrest.flask')


class FlaskUnRest(object):
    def __init__(self, app):
        self.app = app

    def register_route(self, path, method, parameters, fun):
        """Register fun for `path` for `method` with and without `parameters`
        """
        log.info('Registering route for %s for %s' % (path, method))
        path_with_params = path + '/' + '/'.join(
            '<%s>' % param.name for param in parameters)
        log.info(
            'Registering route for %s for %s' % (path_with_params, method))
        if self.app.view_functions.pop(fun.__name__, None):
            log.info('Overriding route %s' % fun.__name__)
        self.app.route(path, methods=[method])(
            self.app.route(path_with_params, methods=[method])(
                fun))

    def request_json(self):
        if not request.is_json:
            return None
        return request.data

    def send_json(self, json):
        return current_app.response_class(
            (json, '\n'),
            mimetype=current_app.config['JSONIFY_MIMETYPE']
        )

    def send_error(self, message, status_code):
        return jsonify(message), status_code
