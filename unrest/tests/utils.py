import json as jsonlib
from tempfile import NamedTemporaryFile

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from ..unrest import UnRest
from .model import Base, Fruit, Tree, fill_data

f = NamedTemporaryFile()
db_url = 'sqlite:///%s' % f.name

engine = create_engine(db_url)
Session = sessionmaker()
Session.configure(bind=engine)
session = scoped_session(Session)


class UnRestTestCase(object):
    def setUp(self):
        super().setUp()
        self.engine = engine
        self.session = session
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        fill_data(self.session)
        self.rest = self.make_unrest()

    def tearDown(self):
        self.session.remove()

    def make_unrest(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree)
        rest(Fruit)
        return rest

    def json_fetch(self, *args, **kwargs):
        kwargs.setdefault('method', 'GET')
        json = kwargs.pop('json', '')
        if json:
            kwargs.setdefault('body', jsonlib.dumps(json))
            kwargs.setdefault('headers', {'Content-Type': 'application/json'})

        response = self.fetch(*args, **kwargs)
        code = response.code
        self.assertEqual(
            response.headers.get('Content-Type'), 'application/json'
        )
        rv = jsonlib.loads(response.body.decode('utf-8'))
        return code, rv
