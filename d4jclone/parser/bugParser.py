import linecache
import json
from pathlib import Path
from d4jclone.config import PROJECTDIR


class Bug():
    def __init__(self, project, _id, rev_buggy, rev_fixed, rev_date_fixed, external_id, url):
        self.project = project
        self.id = _id
        self.rev_buggy = rev_buggy
        self.rev_fixed = rev_fixed
        self.rev_date_fixed = rev_date_fixed
        self.external_id = external_id
        self.url = url

def parseBug(project, bug_id):
    path = Path(PROJECTDIR) / project / 'bugs.csv'
    bug = linecache.getline(str(path), int(bug_id)+1).split(',')
    return Bug(project, bug_id, bug[1], bug[2], bug[3], bug[4], bug[5][:-1])

def getModifiedSources(bug):
    srcs = []
    path = Path(PROJECTDIR) / bug.project / 'modified_sources.json'
    with open(path) as json_file:
        modified = json.load(json_file)
        srcs = modified[bug.external_id]
    srcs.sort()
    return srcs