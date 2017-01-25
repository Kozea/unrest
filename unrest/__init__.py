import logging

from .rest import Rest

log = logging.getLogger('unrest')


class UnRest(object):
    """Root path on /path/version/ if version else /path/ """

    class RestError(Exception):
        def __init__(self, status, message):
            self.status = status
            self.message = message

    def __init__(self,
                 app=None, session=None,
                 path='/api', version='', framework=None):
        self.path = path
        self.version = version
        self._framework = framework
        if app is not None:
            self.init_app(app)
        if session is not None:
            self.init_session(session)

    def init_app(self, app):
        self.app = app
        if self._framework:
            self.framework = self._framework(app)
        else:
            try:
                from flask import Flask
            except ImportError:
                pass
            else:
                if isinstance(app, Flask):
                    from .flask_framework import FlaskUnRest
                    self.framework = FlaskUnRest(app)
        if not self.framework:
            raise NotImplementedError(
                'Your framework %s is not recognized. '
                'Please provide a framework argument to UnRest' % type(app))

    def init_session(self, session):
        self.session = session

    @property
    def root_path(self):
        if self.version:
            return '/'.join((self.path, self.version))
        return self.path

    @property
    def all(self):
        return ['GET', 'PUT', 'POST', 'DELETE']

    def raise_error(self, status, message):
        raise self.RestError(status, message)

    def __call__(self, *args, **kwargs):
        rest = Rest(self, *args, **kwargs)
        return rest
