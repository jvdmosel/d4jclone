from setuptools import setup
import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))
env = os.environ
with open('d4jclone/config.py', 'w') as config:
    config.write('ENV = {\n\t\'BASEDIR\': \'' + BASEDIR + '\','
                 + '\n\t\'SCRIPTDIR\': \'' + BASEDIR + '/d4jclone\','
                 + '\n\t\'REPODIR\': \'' + BASEDIR + '/project_repos\','
                 + '\n\t\'PROJECTDIR\': \'' + BASEDIR + '/d4jclone/projects\','
                 + '\n\t\'TZ\': \'America/Los_Angeles\','
                 + '\n}')

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