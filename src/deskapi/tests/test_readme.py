import json
import os.path
import re
import unittest

import httpretty
import manuel.codeblock
import manuel.doctest
import manuel.testcase
import manuel.testing

from deskapi.six import parse_qs
from deskapi.tests.util import fixture


class ReadmeCase(object):

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


m = manuel.doctest.Manuel()

def load_tests(*args):

    m = manuel.codeblock.Manuel()
    m += manuel.doctest.Manuel()
    m += manuel.testcase.SectionManuel()

    return manuel.testing.TestSuite(
         m,
         './../../../README.rst',
         TestCase=type(
             'ReadmeTestCase',
             (ReadmeCase, manuel.testing.TestCase),
             {},
        ),
    )

if __name__ == '__main__':
    unittest.TextTestRunner().run(load_tests())
