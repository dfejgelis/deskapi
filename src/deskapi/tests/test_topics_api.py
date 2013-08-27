# -*- coding: utf-8 -*-

import json
import re
from deskapi.six import (
    TestCase,
    unicode_str,
)

import httpretty

from deskapi import models
from deskapi.tests.util import fixture

class DeskApi2TopicTests(TestCase):

    def setUp(self):

        httpretty.httpretty.reset()
        httpretty.enable()

        # register topic list
        httpretty.register_uri(
            httpretty.GET,
            'https://testing.desk.com/api/v2/topics',
            body=fixture('topic_list_page_1.json'),
            content_type='application/json',
        )

        # register patching the first topic
        httpretty.register_uri(
            httpretty.PATCH,
            'https://testing.desk.com/api/v2/topics/1',
            body=fixture('topic_patch_topic_1.json'),
            content_type='application/json',
        )

        # register creating a new topic
        httpretty.register_uri(
            httpretty.POST,
            'https://testing.desk.com/api/v2/topics',
            body=fixture('topic_create_response.json'),
            content_type='application/json',
        )

        # topic translation list
        httpretty.register_uri(
            httpretty.GET,
            'https://testing.desk.com/api/v2/topics/1/translations',
            body=fixture('topic_translations.json'),
            content_type='application/json',
        )

        # update topic translation
        httpretty.register_uri(
            httpretty.PATCH,
            'https://testing.desk.com/api/v2/topics/1/translations/ja',
            body=fixture('topic_translation_update.json'),
            content_type='application/json',
        )

        # create topic translation
        httpretty.register_uri(
            httpretty.POST,
            'https://testing.desk.com/api/v2/topics/1/translations',
            body=fixture('topic_translation_create.json'),
            content_type='application/json',
        )

    def tearDown(self):

        httpretty.disable()

    def test_topics_returns_collection(self):

        desk_api = models.DeskApi2(sitename='testing')
        topics = desk_api.topics()

        self.assertEqual(len(topics), 2)

    def test_topics_allows_indexing(self):

        desk_api = models.DeskApi2(sitename='testing')
        topics = desk_api.topics()

        first_topic = topics[0]

        self.assertTrue(isinstance(first_topic, models.DeskObject))

    def test_topic_allows_property_access(self):

        desk_api = models.DeskApi2(sitename='testing')
        topics = desk_api.topics()

        first_topic = topics[0]

        self.assertEqual(first_topic.name, 'Customer Support')
        self.assertEqual(first_topic.in_support_center, True)

    def test_topic_translations_returns_collection(self):

        desk_api = models.DeskApi2(sitename='testing')
        topic = desk_api.topics()[0]

        self.assertEqual(len(topic.translations), 2)

    def test_translation_dict_access(self):
        desk_api = models.DeskApi2(sitename='testing')
        topic = desk_api.topics()[0]

        ja = topic.translations['ja']
        self.assertEqual(ja.name, 'Japanese Translation')

    def test_save_topic_translation(self):

        desk_api = models.DeskApi2(sitename='testing')
        topic = desk_api.topics()[0]

        ja = topic.translations['ja']
        self.assertEqual(ja.name, 'Japanese Translation')

        ja.name = '日本語訳'
        updated_ja = ja.save()

        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('topic_translation_update_request.json')),
        )

        self.assertEqual(updated_ja.name, unicode_str('日本語訳'))

    def test_update_topic_translation(self):

        desk_api = models.DeskApi2(sitename='testing')
        topic = desk_api.topics()[0]

        ja = topic.translations['ja']
        self.assertEqual(ja.name, 'Japanese Translation')

        updated_ja = ja.update(
            name='日本語訳',
        )

        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('topic_translation_update_request.json')),
        )

        self.assertEqual(updated_ja.name, unicode_str('日本語訳'))

    def test_create_topic_translation(self):

        desk_api = models.DeskApi2(sitename='testing')
        topic = desk_api.topics()[0]

        es = topic.translations.create(
            name='Traducción español',
            locale='es',
        )

        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('topic_translation_create_request.json')),
        )

        self.assertEqual(es.name, unicode_str('Traducción español'))
        self.assertEqual(es.locale, 'es')

    def test_topic_api_href(self):

        desk_api = models.DeskApi2(sitename='testing')
        topic = desk_api.topics()[0]

        self.assertEqual(topic.api_href, '/api/v2/topics/1')

    def test_save_topic(self):

        desk_api = models.DeskApi2(sitename='testing')
        topic = desk_api.topics()[0]

        topic.name = 'New Name'
        updated_topic = topic.save()

        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('topic_update_request.json')),
        )

        self.assertEqual(updated_topic.name, topic.name)

    def test_update_topic(self):

        desk_api = models.DeskApi2(sitename='testing')
        updated_topic = desk_api.topics()[0].update(
            name='New Name',
        )

        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('topic_update_request.json')),
        )

        self.assertEqual(updated_topic.name, 'New Name')

    def test_create_topic(self):

        desk_api = models.DeskApi2(sitename='testing')
        topics = desk_api.topics()

        new_topic = topics.create(
            name='Social Media',
        )

        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('topic_create_request.json')),
        )

        self.assertEqual(new_topic.name, 'Social Media')

    def test_topics_support_iteration(self):

        desk_api = models.DeskApi2(sitename='testing')

        count = 0
        for topic in desk_api.topics():
            self.assertIsInstance(topic, models.DeskObject)
            count += 1

        self.assertEqual(count, 2)
