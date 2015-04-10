# -*- coding: utf-8 -*-
import unittest

from ApiSDF import app
from ApiSDF.auth import _admin_manager_client
from ApiSDF.utils import format_result


class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()
        cls.api = 'api_tests'
        cls.user = 'user'
        cls.password = 'pass'
        cls.app = app.test_client()
        with _admin_manager_client(cls.app.application) as client:
            client[cls.api].add_user(
                cls.user,
                cls.password,
                roles=[
                    {'role': 'dbOwner', 'db': cls.api}
                ]
            )


class LoggedTest(BaseTest):

    @classmethod
    def setUpClass(cls):
        super(LoggedTest, cls).setUpClass()
        response = cls.app.post('/login', data={
            'email': cls.user,
            'password': cls.password,
            'api': cls.api,
        })
        cls.headers = {
            'X-Email': response.headers['X-Email'],
            'X-Token': response.headers['X-Token']
        }

    @classmethod
    def tearDownClass(cls):
        cls.app.post('/logout', headers=cls.headers, data={'api': cls.api})
        super(LoggedTest, cls).tearDownClass()


class MoviesTest(LoggedTest):

    actors = [
        {'name': u'Pam Grier', 'gender': u'famele'},
        {'name': u'Samuel Jackson', 'gender': u'male'},
        {'name': u'Harvey Keitel', 'gender': u'male'}
    ]

    movies = [
        {'name': u'Jackie Brown', 'year': u'1997'},
        {'name': u'Pulp Fiction', 'year': u'1994'},
        {'name': u'Reservoir Dogs', 'year': u'1992'},
    ]

    @classmethod
    def setUpClass(cls):
        super(MoviesTest, cls).setUpClass()
        with _admin_manager_client(cls.app.application) as client:
            client[cls.api].actors.insert(cls.actors)
            cls.actors = [format_result(actor) for actor in cls.actors]
            for movie in cls.movies:
                movie.update({'actors': [cls.actors[cls.movies.index(movie)]['id']]})
            client[cls.api].movies.insert(cls.movies)
            cls.movies = [format_result(movie) for movie in cls.movies]

    @classmethod
    def tearDownClass(cls):
        with _admin_manager_client(cls.app.application) as client:
            client[cls.api].actors.drop()
            client[cls.api].movies.drop()
        super(MoviesTest, cls).tearDownClass()