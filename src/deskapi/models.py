import json
import os.path
from oauth_hook import OAuthHook
import requests

class DeskError(Exception):
    def __init__(self, status):
        Exception.__init__(self, status)  # Exception is an old-school class
        self.status = status

    def __str__(self):
        return self.status

    def __unicode__(self):
        return unicode(self.__str__())


class DeskSession(object):

    _CLASSES = {}
    _COLLECTIONS = {}

    def __init__(self, sitename, access_token, access_token_secret, consumer_key, consumer_secret):
        self._access_token = access_token
        self._access_token_secret = access_token_secret
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret

        self._sitename = sitename
        self._BASE_URL = 'https://%s.desk.com' % (sitename, )

        self.auth_info = {
            'sitename': self._sitename,
            'access_token': self._access_token,
            'access_token_secret': self._access_token_secret,
            'consumer_key': self._consumer_key,
            'consumer_secret': self._consumer_secret,
        }

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

        url = '%s%s' % (self._BASE_URL, path,)

        request = requests.Request(method.upper(), url, data=json.dumps(request_kwargs))
        oauth_hook = OAuthHook(self._access_token, self._access_token_secret, self._consumer_key,
                               self._consumer_secret, header_auth=True)
        request = oauth_hook(request)
        session = requests.session()
        session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        r = session.send(request.prepare())

        if r.status_code >= 400:
            raise DeskError(str(r.status_code))
        return json.loads(r.content)


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
        kwargs.update(**self.auth_info)

        return object_class(entry, *args, **kwargs)

    def collection(self, link_info, *args, **kwargs):
        """Return a DeskCollection for the link_info."""

        object_class = self._COLLECTIONS.get(
            link_info['class'],
            DeskCollection,
        )

        kwargs.update(**self.auth_info)

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
        page_response = self.request(self._path)
        if self._links is None and page_response.get('_links'):
            self._links = page_response.get('_links')

        while page_response and page_response.get('_embedded', {}).get('entries'):

            for entry in page_response['_embedded']['entries']:
                items.append(
                    self.object(entry)
                )

            if page_response.get('_links', {}).get('next'):
                page_response = self.request(
                    page_response['_links']['next']['href']
                )
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
            )
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
            )
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

        return self.object(response)

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

    @property
    def id(self):
        return int(self._links['self']['href'].split("/")[-1])

    def articles(self):
        if self._links.get('articles'):
            return self.collection(
                self._links.get('articles'),
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
