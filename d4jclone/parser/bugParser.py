import csv
import linecache
from pathlib import Path
from d4jclone.config import ENV


class Bug():
    def __init__(self, project, _id, rev_buggy, rev_fixed, 
                 rev_date_buggy, rev_date_fixed, external_id, url):
        self.project = project
        self.id = _id
        self.rev_buggy = rev_buggy
        self.rev_fixed = rev_fixed
        self.rev_date_buggy = rev_date_buggy
        self.rev_date_fixed = rev_date_fixed
        self.external_id = external_id
        self.url = url

def parseBug(project, bug_id):
    path = Path(ENV['PROJECTDIR']) / project / 'bugs.csv'
    bug = linecache.getline(str(path), int(bug_id)+1).split(',')
    return Bug(project, bug_id, bug[1], bug[2], bug[3], bug[4], bug[5], bug[6][:-1])

def getModifiedSources(bug):
    srcs = parseLines(bug, 'modified_classes', '.src')
    srcs.sort()
    return srcs

def getLoadedClasses(bug, postfix = 'src'):
    srcs = parseLines(bug, 'loaded_classes', '.' + postfix)
    return srcs

def getRelevantTests(bug):
    tests = parseLines(bug, 'relevant_tests')
    return tests

def getLayout(bug, version):
    with open(ENV['PROJECTDIR'] + '/' + bug.project + '/dir-layout.csv', 'r') as layout_file:
        csv_reader = csv.reader(layout_file)
        rev = bug.rev_buggy if version == 'b' else bug.rev_fixed
        # filters csv file for row of unique revision
        layout = next(filter(lambda x: rev in x, csv_reader))
        return (layout[1],layout[2])

def parseLines(bug, dir_name, postfix = ''):
    lines = []
    path = Path(ENV['PROJECTDIR']) / bug.project / dir_name / (str(bug.id) + postfix)
    with open(path, 'r') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    return lines