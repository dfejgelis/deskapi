# -*- coding: utf-8 -*-

from unittest2 import TestCase

import requests

from deskapi import models


class DeskSessionTests(TestCase):

    def test_requests_session_created_if_omitted(self):

        session = models.DeskSession()

        self.assertTrue(session._session)
        self.assertIsInstance(session._session, requests.Session)

    def test_auth_consumed_for_session(self):

        session = models.DeskSession(auth=('foo', 'bar'))

        self.assertIsInstance(session._session, requests.Session)
        self.assertEqual(session._session.auth, ('foo', 'bar'))
