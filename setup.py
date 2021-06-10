from setuptools import setup, find_namespace_packages
from pathlib import Path
import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))
with open('d4jclone/config.py', 'w') as config:
    config.write('BASEDIR = ' + '\'' + BASEDIR + '\'\n')
    config.write('SCRIPTDIR =' + '\'' + BASEDIR + '/d4jclone\'\n')
    config.write('REPODIR =' + '\'' + BASEDIR + '/project_repos\'\n')
    config.write('PROJECTDIR =' + '\'' + BASEDIR + '/d4jclone/projects\'\n')

setup(
    name = 'd4jclone',
    version='1.0',
    packages=['d4jclone', 'd4jclone.util', 'd4jclone.parser', 'd4jclone.core'],
    entry_points={
        'console_scripts': [
            'd4jclone = d4jclone.runner:main'
        ]},
    install_requires=[
          'gitpython',
    ]
)