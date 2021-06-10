from pathlib import Path

import yaml
from mongoengine import connect


def dbConnect():
    # load credentials
    credentials = yaml.load(open(Path.cwd() / 'credentials.yml'), Loader=yaml.FullLoader)
    
    # connect to database
    loc = {'host': credentials['db']['host'],
           'port': int(credentials['db']['port']),
           'db': credentials['db']['name'],
           'username': credentials['db']['user'],
           'password': credentials['db']['pw'],
           'authentication_source': credentials['db']['auth'],
           'connect': False}
    connect(**loc)
