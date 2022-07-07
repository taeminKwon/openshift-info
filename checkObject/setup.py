# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
config = {
    'description': 'checkobject',
    'author': 'Taemin Kwon',
    'url': 'https://github.com/taeminKwon/openshift-check.git',
    'download_url' : 'https://github.com/taeminKwon/openshift-check.git',
    'author_email': 'taemin.kwon.81@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['checkobject'],
    'scripts': [],
    'name': 'OpenShift components info'
}

setup(**config)




