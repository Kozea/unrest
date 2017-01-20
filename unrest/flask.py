import logging
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
        self.app.route(path, methods=[method])(
            self.app.route(path_with_params, methods=[method])(
                fun))
