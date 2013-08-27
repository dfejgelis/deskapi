from deskapi.six import unittest


def additional_tests():
    return unittest.defaultTestLoader.discover('.')
