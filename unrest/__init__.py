import logging

from .rest import Rest

log = logging.getLogger('unrest')


class UnRest(object):
    """Root path on /path/version/ if version else /path/ """
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
                    from .flask import FlaskUnRest
                    self.framework = FlaskUnRest(app)
        if not self.framework:
            raise NotImplemented(
                'Your framework %s is not recognized. '
                'Please provide a framework argument to UnRest' % type(app))

    def init_session(self, session):
        self.session = session

    @property
    def root_path(self):
        return '/'.join((self.path, self.version))

    def __call__(self, *args, **kwargs):
        rest = Rest(self, *args, **kwargs)
        return rest
