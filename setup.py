from __future__ import with_statement

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    with open('ircclient/version.txt') as f:
        return f.read().strip()


def get_readme():
    try:
        with open('README.rst') as f:
            return f.read().strip()
    except IOError:
        return ''

setup(
    name='ircclient',
    version=get_version(),
    description='Simple client interface.',
    long_description=get_readme(),
    author='Jeong YunWon',
    author_email='jeong+ircclient@youknowone.org',
    url='https://github.com/youknowone/ircclient',
    packages=(
        'ircclient',
    ),
    package_data={
        'ircclient': ['version.txt']
    },
    install_requires=[
        'distribute',
    ],
)
