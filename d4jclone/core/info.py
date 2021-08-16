from pathlib import Path

from d4jclone.config import ENV
from d4jclone.parser.bugParser import (getModifiedSources, getTriggerTests,
                                       parseBug)
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.input_validation import is_valid_pid
from d4jclone.util.projects import projects

sep = '\n'+ '-' * 80

def project_info(project_id):
    project = parseProject(project_id)
    print('Summary of configuration for Project: ' + project.id + sep)
    print('    Script dir: ' + ENV['SCRIPTDIR'])
    print('      Base dir: ' + ENV['BASEDIR'])
    print('      Repo dir: ' + ENV['REPODIR'] + sep)
    print('    Project ID: ' + project.id)
    print('       Program: ' + project.program)
    print('    Build File: ' + project.build_file + sep)
    print('           Vcs: ' + project.vcs)
    print('    Repository: ' + str(Path(ENV['REPODIR']) / (projects.get(project.id) + '.git')))
    print('     Commit db: ' + str(Path(ENV['SCRIPTDIR']) / 'projects' / project.id / 'bugs.csv'))
    print('Number of bugs: ' + str(project.number_of_bugs) + sep)

def bug_info(project_id, bug_id):
    bug = parseBug(project_id, bug_id)
    print('\nSummary for Bug: ' + project_id + '-' + str(bug.id) + sep)
    print('Revision ID (fixed version):\n' + bug.rev_fixed + sep)
    print('Revision date (fixed version):\n' + bug.rev_date_fixed + sep)
    print('Bug report id:\n' + bug.external_id + sep)
    print('Bug report url:\n' + bug.url + sep)
    trigger_tests = getTriggerTests(project_id, bug_id)
    print('Root cause in triggering tests:')
    if trigger_tests != None:
        for test in trigger_tests.keys():
            print(' - ' + test + '\n   --> ' + trigger_tests[test])
        print('-' * 80)
    else:
        print('UNKNOWN' + sep)
    srcs = getModifiedSources(project_id, bug_id)
    if len(srcs) > 0:
        srcs = '\n - '.join(srcs)
    else:
        srcs = 'UNKNOWN'
    print('List of modified sources:\n - ' + srcs + sep)
        
def info(project_id, bug_id = None):
    if is_valid_pid(project_id):
        project = parseProject(project_id)
        project_info(project_id)
        if bug_id != None:
            if 0 < int(bug_id) <= project.number_of_bugs+1:
                bug_info(project_id, bug_id)
            else:
                raise Exception('Error: ' + project_id + '-' + bug_id  + ' is a non-existent bug')
    else:
        raise Exception('Invalid project_id: ' + project_id)
