import os


def fixture(filename):
    """Locate and return the contents of a JSON fixture."""

    absolute_filename = os.path.join(
        os.path.dirname(__file__),
        'fixtures',
        filename,
    )

    with open(absolute_filename, 'r') as fixture_file:

        return fixture_file.read()
