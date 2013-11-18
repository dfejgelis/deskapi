# -*- coding: utf-8 -*-

import json
import os
import re

from deskapi.six import (
    TestCase,
    parse_qs,
    unicode_str,
)

import httpretty

from deskapi import models
from deskapi.tests.util import fixture


class DeskApi2ArticleTests(TestCase):

    NUM_ARTICLES = 75
    PER_PAGE = 50

    def _article_page(self, method, uri, headers):

        previous = next = 'null'

        if '?' in uri:
            page = int(parse_qs(uri.split('?', 1)[1])['page'][0])
        else:
            page = 1
        start_index = (page - 1) * self.PER_PAGE

        template = fixture('article_template.json')
        entries = [
            json.loads(
                template % dict(
                    index=index + 1,
                )
            )
            for index in
            range(start_index,
                  min(self.NUM_ARTICLES, page * self.PER_PAGE))
        ]

        if page > 1:
            previous = json.dumps({
                'href': '/api/v2/articles?page=%s' % (page - 1),
                'class': 'page',
            })
        if (page * self.PER_PAGE < self.NUM_ARTICLES):
            next = json.dumps({
                'href': '/api/v2/articles?page=%s' % (page + 1),
                'class': 'page',
            })

        content = fixture('article_page_template.json') % dict(
            entries=json.dumps(entries),
            next=next,
            previous=previous,
            num_entries=self.NUM_ARTICLES,
        )
        return (200, headers, content)

    def setUp(self):
        httpretty.httpretty.reset()
        httpretty.enable()

        # article pagination
        httpretty.register_uri(
            httpretty.GET,
            re.compile(r'https://testing.desk.com/api/v2/articles(\?page=\d+)?$'),
            body=self._article_page,
            content_type='application/json',
        )

        # article creation
        httpretty.register_uri(
            httpretty.POST,
            re.compile('https://testing.desk.com/api/v2/articles(\?page=\d+)?$'),
            body=fixture('article_create_response.json'),
            content_type='application/json',
        )

        # article update
        httpretty.register_uri(
            httpretty.PATCH,
            'https://testing.desk.com/api/v2/articles/1',
            body=fixture('article_update_response.json'),
            content_type='application/json',
        )

        # article translations
        httpretty.register_uri(
            httpretty.GET,
            'https://testing.desk.com/api/v2/articles/1/translations',
            body=fixture('article_translations.json'),
            content_type='application/json',
        )

        # translation creation
        httpretty.register_uri(
            httpretty.POST,
            'https://testing.desk.com/api/v2/articles/1/translations',
            body=fixture('article_translation_create_response.json'),
            content_type='application/json',
        )

        # translation update
        httpretty.register_uri(
            httpretty.PATCH,
            'https://testing.desk.com/api/v2/articles/1/translations/es',
            body=fixture('article_translation_update_response.json'),
            content_type='application/json',
        )

        # single article
        httpretty.register_uri(
            httpretty.GET,
            'https://testing.desk.com/api/v2/articles/42',
            body=fixture('article_show.json'),
            content_type='application/json',
        )

    def tearDown(self):

        httpretty.disable()

    def test_articles_pagination(self):

        desk_api = models.DeskApi2(sitename='testing')
        articles = desk_api.articles()

        self.assertEqual(len(articles), 75)
        self.assertEqual(len(httpretty.httpretty.latest_requests), 2)

    ## def test_incremental_cache_filling(self):

    ##     article = models.DeskApi2(sitename='testing').articles()[0]
    ##     self.assertEqual(len(httpretty.httpretty.latest_requests), 1)

    def test_article_property_access(self):

        article = models.DeskApi2(sitename='testing').articles()[0]

        self.assertEqual(article.subject, "Subject 1")

    def test_article_creation(self):

        articles = models.DeskApi2(sitename='testing').articles()

        new_article = articles.create(
            subject='Social Media',
        )

        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('article_create_request.json')),
        )
        self.assertEqual(httpretty.last_request().path, '/api/v2/articles')
        self.assertEqual(new_article.subject, 'Social Media')

    def test_article_save(self):

        desk_api = models.DeskApi2(sitename='testing')
        article = desk_api.articles()[0]

        article.subject = 'New Subject'

        updated_article = article.save()
        self.assertEqual(updated_article.subject, 'New Subject')

        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('article_update_request.json')),
        )

    def test_article_update(self):

        desk_api = models.DeskApi2(sitename='testing')
        updated_article = desk_api.articles()[0].update(
            subject='New Subject',
        )

        self.assertEqual(updated_article.subject, 'New Subject')

        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('article_update_request.json')),
        )

    def test_article_translation_dict_access(self):

        desk_api = models.DeskApi2(sitename='testing')
        article = desk_api.articles()[0]

        es = article.translations['es']
        self.assertEqual(es.subject, 'Tema de Ayuda')

    def test_article_translation_containment_checking(self):

        desk_api = models.DeskApi2(sitename='testing')
        article = desk_api.articles()[0]

        self.assertTrue('es' in article.translations)

    def test_article_translation_creation(self):

        desk_api = models.DeskApi2(sitename='testing')
        article = desk_api.articles()[0]

        ja = article.translations.create(
            locale='ja',
            subject='日本語訳',
        )

        self.assertEqual(ja.subject, unicode_str('日本語訳'))

    def test_article_translation_save(self):

        desk_api = models.DeskApi2(sitename='testing')
        article = desk_api.articles()[0]

        es = article.translations['es']
        es.subject = 'Actualizada la traducción española'
        updated_es = es.save()

        self.assertEqual(
            updated_es.subject,
            unicode_str('Actualizada la traducción española'),
        )
        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('article_translation_update_request.json')),
        )

    def test_article_translation_update(self):

        desk_api = models.DeskApi2(sitename='testing')
        article = desk_api.articles()[0]

        es = article.translations['es']
        updated_es = es.update(
            subject = 'Actualizada la traducción española',
        )

        self.assertEqual(
            updated_es.subject,
            unicode_str('Actualizada la traducción española'),
        )
        self.assertEqual(
            json.loads(unicode_str(httpretty.last_request().body)),
            json.loads(fixture('article_translation_update_request.json')),
        )

    def test_get_article_by_id(self):

        desk_api = models.DeskApi2(sitename='testing')
        article = desk_api.articles().by_id(42)

        self.assertIsInstance(article, models.DeskObject)
