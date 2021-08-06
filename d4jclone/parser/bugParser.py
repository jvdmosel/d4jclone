import linecache
from pathlib import Path
from d4jclone.config import ENV


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
    path = Path(ENV['PROJECTDIR']) / project / 'bugs.csv'
    bug = linecache.getline(str(path), int(bug_id)+1).split(',')
    return Bug(project, bug_id, bug[1], bug[2], bug[3], bug[4], bug[5][:-1])

def getModifiedSources(bug):
    srcs = parseLines(bug, 'modified_classes', '.src')
    srcs.sort()
    return srcs

def parseLines(bug, dir_name, postfix = None):
    lines = []
    path = Path(ENV['PROJECTDIR']) / bug.project / dir_name / (str(bug.id) + postfix)
    with open(path, 'r') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    return lines