import json as jsonlib
import re

from sqlalchemy import event
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from ..model import Base, fill_data


def implement_sqlite_regexp(engine):
    def re_fn(expr, item):
        if not item:
            return
        reg = re.compile(expr, re.I)
        return reg.search(item) is not None

    @event.listens_for(engine, "begin")
    def do_begin(conn):
        conn.connection.create_function('REGEXP', 2, re_fn)


class UnRestClient(object):
    @classmethod
    def setUpClass(cls):
        cls.db()

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def db(cls):
        cls.db_url = 'sqlite://'

        cls.engine = create_engine(cls.db_url)
        implement_sqlite_regexp(cls.engine)
        Session = sessionmaker()
        Session.configure(bind=cls.engine)
        cls.session = scoped_session(Session)

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        fill_data(self.session)

    def tearDown(self):
        self.session.remove()

    def fetch(self, *args, **kwargs):
        kwargs.setdefault('method', 'GET')
        json = kwargs.pop('json', None)
        if json is not None:
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
