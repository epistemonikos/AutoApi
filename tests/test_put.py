# -*- coding: utf-8 -*-
import json
import unittest

from ApiSDF.auth import _admin_manager_client
from utils import MoviesTest


class TestPutResource(MoviesTest):

    def test_put_invalid_id(self):
        response = self.app.put('/%s/movies/a1' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertDictContainsSubset({'message': u'Resource "a1" is invalid'}, json.loads(response.data))

    def test_put_not_found_id(self):
        response = self.app.put('/%s/actors/%s' % (self.api, self.movies[0]['id']), headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data)
        self.assertDictContainsSubset(
            {'message': u'Resource "%s" not found' % self.movies[0]['id']},
            response_json
        )

    def test_put(self):
        self.movies[0]['country'] = 'USA'
        response = self.app.put(
            '/%s/movies/%s' % (self.api, self.movies[0]['id']),
            headers=self.headers,
            data=self.movies[0]
        )
        self.assertEqual(response.status_code, 204)
        response = self.app.get('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=self.headers)
        response_json = json.loads(response.data)
        self.assertEqual(self.movies[0], response_json)

    def test_put_nested(self):
        self.movies[1]['country'] = 'USA'
        response = self.app.put(
            '/%s/actors/%s/movies/%s' % (self.api, self.actors[1]['id'], self.movies[1]['id']),
            headers=self.headers,
            data=self.movies[1]
        )
        self.assertEqual(response.status_code, 204)
        response = self.app.get('/%s/movies/%s' % (self.api, self.movies[1]['id']), headers=self.headers)
        response_json = json.loads(response.data)
        self.assertEqual(self.movies[1], response_json)


class TestPutCollection(MoviesTest):

    def test_put(self):
        response = self.app.put('/%s/movies' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertDictContainsSubset(
            {'message': u'Not supported collection update/replace'},
            json.loads(response.data)
        )
