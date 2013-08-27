import csv
import json
import os.path

import requests


class DeskSession(object):

    _CLASSES = {}
    _COLLECTIONS = {}

    def __init__(self, sitename=None, session=None, auth=None):

        if sitename is None:
            raise Exception()

        self._sitename = sitename
        self._BASE_URL = 'https://%s.desk.com' % (sitename, )

        self._session = session

        if self._session is None:
            self._session = requests.Session()
            self._session.auth = auth
            self._session.headers.update({
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                })

    def request(self, path, method='GET', params=None, data=None):

        if path[0] != '/':
            path = '/api/v2/%s' % (path,)

        request_kwargs = {}

        ## --- Someday we may want to do GETs with params; when we do,
        ## --- this may be helpful

        ## if params:
        ##     request_kwargs['params'] = params

        if data:
            request_kwargs['data'] = data

        return self._session.request(
            method,
            '%s%s' % (self._BASE_URL, path,),
            verify=False,
            **request_kwargs
        )

    @classmethod
    def register_class(cls, name):
        """Register a DeskObject subclass for a given name."""

        def wrapper(klass):

            ## --- Somday we may need customized behavior for Objects

            ## if issubclass(klass, DeskObject):
            ##     cls._CLASSES[name] = klass

            if issubclass(klass, DeskCollection):
                cls._COLLECTIONS[name] = klass

            return klass

        return wrapper

    def object(self, entry, *args, **kwargs):
        """Return a DeskObject for the given entry."""

        object_class = self._CLASSES.get(
            entry.get('_links', {}).get('self', {}).get('class'),
            DeskObject,
        )

        kwargs['session'] = self._session
        kwargs['sitename'] = self._sitename

        return object_class(entry, *args, **kwargs)

    def collection(self, link_info, *args, **kwargs):
        """Return a DeskCollection for the link_info."""

        object_class = self._COLLECTIONS.get(
            link_info['class'],
            DeskCollection,
        )

        kwargs['session'] = self._session
        kwargs['sitename'] = self._sitename

        return object_class(link_info['href'], *args, **kwargs)


class DeskApi2(DeskSession):

    def topics(self):

        return self.collection({
            'class': 'topic',
            'href': 'topics',
        })

    def articles(self):

        return self.collection({
            'class': 'article',
            'href': 'articles',
        })


class DeskCollection(DeskSession):

    def __init__(self, path, **kwargs):

        self._path = path
        self._cache = None
        self._links = None

        super(DeskCollection, self).__init__(**kwargs)

    def items(self):

        # XXX support partial/incremental cache filling
        if self._cache is None:
            self._cache = self._fill_cache()

        return self._cache

    def _fill_cache(self):

        items = []
        page_response = self.request(self._path).json()
        if self._links is None and page_response.get('_links'):
            self._links = page_response.get('_links')

        while page_response and page_response.get('_embedded', {}).get('entries'):

            for entry in page_response['_embedded']['entries']:
                items.append(
                    self.object(entry, session=self._session)
                )

            if page_response.get('_links', {}).get('next'):
                page_response = self.request(
                    page_response['_links']['next']['href']
                ).json()
            else:
                page_response = None

        return items

    def __len__(self):

        return len(self.items())

    def create(self, **kwargs):
        """Create a new item in the Collection and return it."""

        return self.object(
            self.request(
                self._path,
                method='POST',
                data=json.dumps(kwargs),
            ).json()
        )

    def __getitem__(self, n):

        return self.items()[n]

    def __contains__(self, key):

        return key in self.items()

    def by_id(self, id):
        """Return an item of this collection based on its ID."""

        return self.object(
            self.request(
                '%s/%s' % (self._path, id),
                method='GET',
            ).json()
        )


class DeskObject(DeskSession):

    def __init__(self, entry, **kwargs):

        self._entry = entry
        self._links = entry['_links']
        self._changed = {}

        super(DeskObject, self).__init__(**kwargs)

    @property
    def api_href(self):
        """Return the API href for this object."""

        return self._links['self']['href']

    def save(self):
        """Save this Desk object with new assignments."""

        return self.update(**self._changed)

    def update(self, **kwargs):
        """Update this Desk object with kwargs, returning an updated version."""

        response = self.request(
            self.api_href,
            method='patch',
            data=json.dumps(kwargs),
        )

        return self.object(response.json())

    def __getattr__(self, key):

        return self._entry[key]

    def __setattr__(self, key, value):

        if key in self.__dict__ or key.startswith('_'):
            return super(DeskObject, self).__setattr__(key, value)

        self._entry[key] = self._changed[key] = value

    @property
    def translations(self):

        return self.collection(
            self._links['translations'],
        )


@DeskSession.register_class('topic')
class DeskTopicCollection(DeskCollection):

    def create(self, **kwargs):

        create_kwargs = {
            "name": '',
            "allow_questions": False,
            "in_support_center": False,
        }

        create_kwargs.update(kwargs)

        return super(DeskTopicCollection, self).create(**create_kwargs)


@DeskSession.register_class('article_translation')
@DeskSession.register_class('topic_translation')
class DeskTranslationCollection(DeskCollection):

    def __init__(self, *a, **kw):

        super(DeskTranslationCollection, self).__init__(*a, **kw)

        self._locale_cache = None

    def items(self):

        if self._locale_cache is None:
            items = super(DeskTranslationCollection, self).items()

            self._locale_cache = dict([
                (t.locale, t)
                for t in items
            ])

        return self._locale_cache
