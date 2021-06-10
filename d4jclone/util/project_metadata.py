import json
from pathlib import Path

from d4jclone.util.projects import projects
from d4jclone.config import PROJECTDIR


def createMetadata():
    for project in projects.keys():
        path = Path(PROJECTDIR) / project
        metadata = {}
        metadata['id'] = project
        metadata['program'] = projects.get(project)
        metadata['build_file'] = str(path / (project + '.build.xml'))
        metadata['vcs'] = 'Git'
        with open(path / 'bugs.csv') as f:
            metadata['number_of_bugs'] = str(sum(1 for line in f) - 1)
        with open(path /  'metadata.json', 'w') as json_file:
            json.dump(metadata, json_file, indent=4)