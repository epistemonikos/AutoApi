# -*- coding: utf-8 -*-
import unittest
import json

from auto_api.app import app
from auto_api.auth import _admin_manager_client
from auto_api.utils import format_result


class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()
        cls.api = 'api_tests'
        cls.user = 'user'
        cls.password = 'pass'
        cls.app = app.test_client()
        cls.add_user(cls.api, cls.user, cls.password, ['admin'])

    @classmethod
    def tearDownClass(cls):
        with _admin_manager_client(cls.app.application) as client:
            client[cls.api].authenticate(cls.user, cls.password)
            client.drop_database(cls.api)
        super(BaseTest, cls).tearDownClass()

    @classmethod
    def response_to_headers(cls, response):
        return {
            'X-Email': response.headers['X-Email'],
            'X-Token': response.headers['X-Token']
        }

    @classmethod
    def add_user(cls, api, user, password, roles):
        with _admin_manager_client(cls.app.application) as client:
            client[api].add_user(user, password, customData={'roles': roles})

    @classmethod
    def remove_user(cls, api, user):
        with _admin_manager_client(cls.app.application) as client:
            client[api].remove_user(user)

    def get_admin_headers(self):
        return self.response_to_headers(
            self.app.post('/login', data={
                'email': self.app.application.config['MONGO_ADMIN'],
                'password': self.app.application.config['MONGO_ADMIN_PASS'],
                'api': 'admin',
            })
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
        cls.headers = cls.response_to_headers(response)

    @classmethod
    def tearDownClass(cls):
        cls.app.post('/logout', headers=cls.headers, data={'api': cls.api})
        super(LoggedTest, cls).tearDownClass()

    def _count_test(self, path, amount):
        response = self.app.get('/%s/%s' % (self.api, path), headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertEqual(amount, len(response_json))
        return response_json


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
    def _clean_movies_and_actors(cls):
        with _admin_manager_client(cls.app.application) as client:
            client[cls.api].actors.drop()
            client[cls.api].movies.drop()
            client[cls.api].stars.drop()

    @classmethod
    def setUpClass(cls):
        super(MoviesTest, cls).setUpClass()
        cls._clean_movies_and_actors()
        with _admin_manager_client(cls.app.application) as client:
            client[cls.api].actors.insert(cls.actors)
            cls.actors = [format_result(actor) for actor in cls.actors]
            for movie in cls.movies:
                movie.update({'actors': cls.actors[cls.movies.index(movie)]['id']})
            client[cls.api].movies.insert(cls.movies)
            cls.movies = [format_result(movie) for movie in cls.movies]

    @classmethod
    def tearDownClass(cls):
        cls._clean_movies_and_actors()
        super(MoviesTest, cls).tearDownClass()
