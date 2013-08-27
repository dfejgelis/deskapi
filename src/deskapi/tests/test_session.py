# -*- coding: utf-8 -*-

from deskapi.six import TestCase
import requests

from deskapi import models


class DeskSessionTests(TestCase):

    def test_requests_session_created_if_omitted(self):

        session = models.DeskSession(sitename='testing')

        self.assertTrue(session._session)
        self.assertIsInstance(session._session, requests.Session)

    def test_auth_consumed_for_session(self):

        session = models.DeskSession(sitename='testing', auth=('foo', 'bar'))

        self.assertIsInstance(session._session, requests.Session)
        self.assertEqual(session._session.auth, ('foo', 'bar'))

    def test_sitename_required(self):

        with self.assertRaises(Exception):

            models.DeskSession()

    def test_sitename_sets_base_url(self):

        session = models.DeskSession(sitename='example')

        self.assertEqual(session._sitename, 'example')
        self.assertEqual(session._BASE_URL, 'https://example.desk.com')

    def test_sitename_propagated_for_collection(self):

        session = models.DeskSession(sitename='example')

        collection = session.collection({
            'class': 'Testing',
            'href': '/api/v2/blarf',
        })

        self.assertEqual(session._sitename, collection._sitename)

    def test_sitename_propagated_for_object(self):

        session = models.DeskSession(sitename='example')

        collection = session.object({
            '_links': {},
        })
        self.assertEqual(session._sitename, collection._sitename)
