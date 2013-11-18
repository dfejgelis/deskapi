========
Desk API
========

.. image:: https://travis-ci.org/eventbrite/deskapi.png?branch=master
   :target: https://travis-ci.org/eventbrite/deskapi
   :alt: Build Status

.. image:: https://coveralls.io/repos/eventbrite/deskapi/badge.png?branch=master
   :target: https://coveralls.io/r/eventbrite/deskapi?branch=master
   :alt: Test Coverage

deskapi is a Python wrapper around the `Desk.com REST API`_. It
provides Python wrappers for articles, topics, and translations.
deskapi is compatible with Python 2.6, 2.7, and 3.3.

.. _`Desk.com REST API`: http://dev.desk.com/


Installation
============

deskapi is installable from PyPI_ with ``easy_install`` or pip_.

::

  $ pip install deskapi

This will download the latest release, along with requests_, which it
depends on.

.. _PyPI: https://pypi.python.org/pypi/deskapi
.. _pip: http://pip-installer.org/
.. _requests: https://pypi.python.org/pypi/requests


Getting Started
===============

Access to the Desk API is managed through a ``DeskSession`` object.
To instantiate a session, you'll need a sitename and authentication
information. If your Desk.com site is http://example.desk.com, your
site name will be ``example``. Authentication information is any `valid
Requests auth object`_. The simplest thing to provide is a username
and password. For example::

  >>> from deskapi.models import DeskApi2

  >>> session = DeskApi2(
  ...     sitename='testing',
  ...     auth=('nathan@example.com', '53kr17')
  ... )

Once you have a session ID, you can retrieve a list of Articles_::

  >>> articles = session.articles()

`Article fields`_ map to Python properties::

  >>> article = articles[0]
  >>> str(article.subject)
  'Subject 1'
  >>> article.in_support_center
  True

Collections and Objects
=======================

deskapi models the information available from Desk API as a set of
"collections" and "objects". The ``articles()`` method on
``DeskSesssion`` returns a *collection*. Collections can be iterated
over, and support indexed access. A collection can create new members
in itself.

Each member of a collection is a Desk Object. Desk Objects support
property access to their fields, as well as updating those fields.

Collections
-----------

Creating Members
~~~~~~~~~~~~~~~~

You can create new members of a collection by calling the ``create``
method on it, passing in fields as keyword arguments.

::

   >>> new_article = articles.create(
   ...     title='New Article',
   ...     body='Some content.',
   ... )

Articles
~~~~~~~~

Articles_ are accessible via the ``articles()`` method on the
``DeskSession``.

::

  >>> articles = session.articles()

Topics
~~~~~~

Topics_ are accessible via the ``topics()`` method on the ``DeskSession``.

Translations
~~~~~~~~~~~~

Translations_ are accessible via the ``translations`` property of
Article objects. The translations collection is slightly different
than other collections. Instead of allowing indexed access, it acts
like a ``dict``, keyed by locale::

  >>> translations = article.translations
  >>> len(translations)
  2
  >>> str(translations['es'].subject)
  'Tema de Ayuda'


.. _`valid Requests auth object`: http://docs.python-requests.org/en/latest/user/authentication/
.. _Articles: http://dev.desk.com/API/articles/
.. _`Article fields`: http://dev.desk.com/API/articles/#show
.. _Translations: http://dev.desk.com/API/articles/#translations-show
.. _Topics: http://dev.desk.com/API/topics/

Objects
-------

Updating Objects
~~~~~~~~~~~~~~~~

You can make changes to an object and save those back to Desk. Calling
``.save()`` will return the saved instance.

::

   >>> article.body = 'Test Content'
   >>> article.save()  # doctest: +ELLIPSIS
   <deskapi.models.DeskObject object at ...>

Alternately you can use the ``update`` method to update the
information in Desk *without* updating the local Python object. The
following is equivalent to the ``save`` example::

   >>> article = article.update(body='Test Content')

Both ``save`` and ``update`` return the updated object.


License
=======

Made available under a BSD license; see LICENSE for details.
