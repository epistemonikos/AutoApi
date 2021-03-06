# -*- coding: utf-8 -*-
import json
from operator import itemgetter
import unittest

from tests import MoviesTest


class TestGetResource(MoviesTest):

    def test_get_not_created(self):
        response = self.app.get('/%s/actors/%s' % (self.api, self.movies[0]['id']), headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset(
            {'message': u'Resource "%s" not found' % self.movies[0]['id']},
            response_json
        )

    def test_get_invalid_id(self):
        response = self.app.get('/%s/movies/a1' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset({'message': u'Resource "a1" is invalid'}, response_json)

    def test_get(self):
        response = self.app.get('/%s/movies/%s' % (self.api, self.movies[0]['id']), headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(self.movies[0], response_json)

    def test_get_nested(self):
        response = self.app.get(
            '/%s/actors/%s/movies/%s' % (self.api, self.actors[0]['id'], self.movies[0]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data or '{}')
        self.assertDictEqual(self.movies[0], response_json)

    def test_get_nested_not_found(self):
        response = self.app.get(
            '/%s/actors/%s/movies/%s' % (self.api, self.actors[0]['id'], self.movies[2]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
        response_json = json.loads(response.data or '{}')
        self.assertDictContainsSubset(
            {'message': u'Resource "%s" not found' % self.movies[2]['id']},
            response_json
        )


class TestGetCollection(MoviesTest):

    def test_get_not_created(self):
        response = self.app.get('/%s/countries' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('[]', response.data)

    def test_get(self):
        response = self.app.get('/%s/movies' % self.api, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual(self.movies, response_json)

    def test_get_nested(self):
        response = self.app.get(
            '/%s/actors/%s/movies' % (self.api, self.actors[0]['id']),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual([self.movies[0]], response_json)


class TestGetCollectionParameters(MoviesTest):

    def test_fiilter(self):
        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'name': u'Pulp Fiction', 'year': u'1994'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual(self.movies[1:2], response_json)

    def test_sort(self):
        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'_sort': 'year'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        movies = sorted(self.movies, key=itemgetter('year'))
        self.assertEqual(len(movies), len(response_json))
        for pos in range(len(movies)):
            self.assertEqual(movies[pos], response_json[pos])

        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'_sort': '-year'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        movies.reverse()
        self.assertEqual(len(movies), len(response_json))
        for pos in range(len(movies)):
            self.assertEqual(movies[pos], response_json[pos])

    def test_limit(self):
        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'_limit': '2'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual(self.movies[:2], response_json)

    def test_skip(self):
        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'_skip': '1'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual(self.movies[1:], response_json)

    def test_regex(self):
        response = self.app.get(
            '/%s/movies' % self.api,
            headers=self.headers,
            query_string={'name': u'Fiction', '_regex': u'name'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual(self.movies[1:2], response_json)

    def test_regex2(self):
        response = self.app.get(
            '/%s/actors' % self.api,
            headers=self.headers,
            query_string={'name': u'.*am.*', '_regex': u'name'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertItemsEqual(self.actors[0:2], response_json)


if __name__ == '__main__':
    unittest.main()
