import json as jsonlib
from tempfile import NamedTemporaryFile

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .model import Base, fill_data


class UnRestTestCase(object):
    @classmethod
    def setUpClass(cls):
        cls.db()

    @classmethod
    def db(cls):
        f = NamedTemporaryFile()
        cls.db_url = 'sqlite:///%s' % f.name

        cls.engine = create_engine(cls.db_url)
        Session = sessionmaker()
        Session.configure(bind=cls.engine)
        cls.session = scoped_session(Session)

    def setUp(self):
        super().setUp()
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        fill_data(self.session)

    def tearDown(self):
        self.session.remove()

    def fetch(self, *args, **kwargs):
        kwargs.setdefault('method', 'GET')
        json = kwargs.pop('json', '')
        if json:
            kwargs.setdefault('body', jsonlib.dumps(json))
            kwargs.setdefault('headers', {'Content-Type': 'application/json'})

        response = self.raw_fetch(*args, **kwargs)
        code = response.code
        if response.body:
            rv = response.body.decode('utf-8')
            if response.headers.get('Content-Type') == 'application/json':
                rv = jsonlib.loads(rv)
        else:
            rv = None
        return code, rv
