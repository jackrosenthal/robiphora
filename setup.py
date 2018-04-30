from setuptools import setup
import os
import codecs
import re

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Get the long description from the README file
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='robiphora',
    version=find_version("robiphora", "__init__.py"),
    description='Anaphora resolution for robots that takes into account '
                'situated context (so... exaphora as well...)',
    long_description=long_description,
    url='https://github.com/jackrosenthal/robiphora',

    author='Jack Rosenthal',
    author_email='jack@rosenth.al',

    license='MIT',

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Science/Research',
        'Topic :: Text Processing :: Linguistic',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='anaphora exaphora linguistics robotics',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['robiphora'],

    python_requires='>=3.6, <4',

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'spacy>=2.0',
    ],

    dependency_links=[
        'https://github.com/explosion/spacy-models/releases/download/'
        'en_core_web_md-2.0.0/en_core_web_md-2.0.0.tar.gz',
    ],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'robiphora=robiphora.__main__:main',
        ],
    },
)
