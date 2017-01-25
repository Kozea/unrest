import logging

from .rest import Rest

log = logging.getLogger('unrest')


class UnRest(object):
    """
    A troubling rest api library for sqlalchemy models.
    This is the main entry point of unrest.

    Common usage is as following:

    ```python
    rest = UnRest(app, session)  # app is your application
    # When called, it instanciate a `Rest` object that will register the
    # REST endpoints. See the `Rest` class.
    rest(Model1)
    rest(Model2)
    ```

    # Arguments
        app: Your web application,
            can be set afterwards using #UnRest.init_app
        session: Your sqlalchemy session,
            can be set afterwards using #UnRest.init_session
            and `init_session` method.
        path: Default '/api', sets the root url path for your endpoints
        version: Adds a version to the root url path if specified
            (i.e. /api/v2)
        framework: Your specific framework class, defaults to auto detect.

    Unrest aims to be framework agnostic.
    It currently works with Flask out of the box, for another web framework
    you will have to implement your own Framework class.
    See `FlaskUnRest` in `flask_framework.py`
    """

    class RestError(Exception):
        """
        Exception raised by rest methods. It's catched by the REST method
        wrapper and will return a `status` http error with the specified
        `message`.
        """
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
        """Sets the app on UnRest if it was missing during instantiation."""
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
        """
        Sets the sqlalchemy session on UnRest
        if it was missing during instantiation.
        """
        self.session = session

    @property
    def root_path(self):
        if self.version:
            return '/'.join((self.path, self.version))
        return self.path

    @property
    def all(self):
        """
        Return all supported methods. Useful for the rest
        `method` keyword argument.
        """
        return ['GET', 'PUT', 'POST', 'DELETE']

    def raise_error(self, status, message):
        """
        Raise an error that will be handled by the rest wrapper, which
        will return a json response with status as HTTP status code
        and message as content.
        """
        raise self.RestError(status, message)

    def __call__(self, *args, **kwargs):
        """Returns a #unrest.Rest instance."""
        rest = Rest(self, *args, **kwargs)
        return rest
