import os


def fixture(filename):
    """Locate and return the contents of a JSON fixture."""

    return file(
        os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            filename,
        ), 'r').read()
