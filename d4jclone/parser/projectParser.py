import json
from pathlib import Path
from d4jclone.config import PROJECTDIR

class Project():
    def __init__(self, _id, program, vcs, build_file, number_of_bugs):
        self.id = _id
        self.program = program
        self.vcs = vcs
        self.build_file = build_file
        self.number_of_bugs = number_of_bugs

def parseProject(project):
    metadata_file = Path(PROJECTDIR) / project / 'metadata.json'
    with open(metadata_file) as json_file:
        metadata = json.load(json_file)
        return Project(metadata['id'], metadata['program'], metadata['vcs'], 
                       metadata['build_file'], int(metadata['number_of_bugs']))