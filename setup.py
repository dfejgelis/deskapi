from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.2'

tests_require = [
    'httpretty==0.6.5',
    'manuel',
]
if sys.version_info < (3, 3):
    tests_require.append('unittest2')

install_requires = [
    'requests',
]


setup(name='deskapi',
      version=version,
      description="",
      long_description=README + '\n\n' + NEWS,
      classifiers = [
        'License :: OSI Approved :: BSD License',
      ],
      keywords='',
      author='Nathan Yergler',
      author_email='nathan@eventbrite.com',
      url='https://github.com/eventbrite/deskapi',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='deskapi.tests',
)
