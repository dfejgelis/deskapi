import sys


if sys.version_info < (3, 0):  # pragma: no cover
    import unittest2 as unittest
    from unittest2 import TestCase
    from urlparse import parse_qs

    def unicode_str(input_string):

        if isinstance(input_string, str):
            return input_string.decode('utf8')

        return input_string

else:  # pragma: no cover
    import unittest
    from unittest import TestCase
    from urllib.parse import parse_qs

    def unicode_str(input_string):

        if isinstance(input_string, bytes):
            return input_string.decode('utf8')

        return input_string
