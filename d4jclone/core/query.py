import csv
import sys

from d4jclone.parser.bugParser import (getLoadedClasses, getModifiedSources,
                                       getRelevantTests, getTriggerTests,
                                       parseBug)
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.input_validation import is_valid_pid

available_fields = [
    'project.id',
    'project.name',
    'project.build.file',
    'project.vcs',
    'project.repository',
    'project.bugs.csv',
    'revision.id.buggy',
    'revision.id.fixed',
    'revision.date.buggy',
    'revision.date.fixed',
    'report.id',
    'report.url',
    'classes.modified',
    'classes.relevant.src',
    'classes.relevant.test',
    'tests.relevant',
    'tests.trigger',
    'tests.trigger.cause'
]

def query(project_id, query = None, file = None, help = False):
    if help:
        print('Available fields: ' + ', '.join(available_fields))
        return
    if is_valid_pid(project_id):
        f = None
        if file == None:
            csv_writer = csv.writer(sys.stdout)
        else:
            f = open(file, 'w')
            csv_writer = csv.writer(f)
        rows = []
        project = parseProject(project_id)
        # bug.id is included in all results
        # same behavior as d4j
        for bug_id in range(1, project.number_of_bugs+1):
            rows.append([str(bug_id)])
        if query != None:
            for field in query.split(','):
                # check if given fields are valid
                if not field in available_fields:
                    raise Exception('Requested field ' + field + ' is invalid')
                # values that are bug independent
                # Assigned project ID
                elif field == 'project.id':
                    apply_to_rows(rows, lambda x: project.id)
                # Original project name
                elif field == 'project.name':
                    apply_to_rows(rows, lambda x: project.program)
                # Location of the d4jclone build file for the project
                elif field == 'project.build.file':
                    apply_to_rows(rows, lambda x: project.build_file)
                # Version control system used by the project
                elif field == 'project.vcs':
                    apply_to_rows(rows, lambda x: project.vcs)
                # Location of the project repository
                elif field == 'project.repository':
                    apply_to_rows(rows, lambda x: project.repository)
                # Location of the CSV containing information on that bug
                elif field == 'project.bugs.csv':
                    apply_to_rows(rows, lambda x: project.bug_db)
                # values that are bug dependent
                # Commit hashes for the buggy version of each bug
                elif field == 'revision.id.buggy':
                    apply_to_rows(rows, lambda bug_id: 
                        parseBug(project.id, bug_id).rev_buggy)
                # Commit hashes for the fixed version of each bug
                elif field == 'revision.id.fixed':
                    apply_to_rows(rows, lambda bug_id: 
                        parseBug(project.id, bug_id).rev_fixed)
                # Date of the buggy commit for each bug
                elif field == 'revision.date.buggy':
                    apply_to_rows(rows, lambda bug_id: 
                        parseBug(project.id, bug_id).rev_date_buggy)
                # Date of the fixed commit for each bug
                elif field == 'revision.date.fixed':
                    apply_to_rows(rows, lambda bug_id: 
                        parseBug(project.id, bug_id).rev_date_fixed)
                # Bug report ID from the version tracker for each bug
                elif field == 'report.id':
                    apply_to_rows(rows, lambda bug_id: 
                        parseBug(project.id, bug_id).external_id)
                # Bug report URL from the version tracker for each bug
                elif field == 'report.url':
                    apply_to_rows(rows, lambda bug_id: 
                        parseBug(project.id, bug_id).url)
                # Classes modified by the bug fix
                elif field == 'classes.modified':
                    apply_to_rows(rows, lambda bug_id: 
                        ';'.join(getModifiedSources(project.id, bug_id)))
                # Source classes loaded by the JVM when executing all triggering tests
                elif field == 'classes.relevant.src':
                    apply_to_rows(rows, lambda bug_id: 
                        ';'.join(getLoadedClasses(project.id, bug_id)))
                # Test classes loaded by the JVM when executing all triggering tests
                elif field == 'classes.relevant.test':
                    apply_to_rows(rows, lambda bug_id: 
                        ';'.join(getLoadedClasses(project.id, bug_id, 'test')))
                # List of relevant tests classes 
                # (a test class is relevant if, when executed, 
                # the JVM loads at least one of the modified classes)
                elif field == 'tests.relevant':
                    apply_to_rows(rows, lambda bug_id: 
                        ';'.join(getRelevantTests(project.id, bug_id)))
                # List of test methods that trigger (expose) the bug
                elif field == 'tests.trigger':
                    apply_to_rows(rows, lambda bug_id: 
                        ';'.join(getTriggerTests(project.id, bug_id).keys()))
                # List of test methods that trigger (expose) the bug, 
                # along with the root cause
                elif field == 'tests.trigger.cause':
                    apply_to_rows(rows, lambda bug_id:
                        ';'.join(['%s --> %s' % (key, value) for (key, value) in getTriggerTests(project.id, bug_id).items()]))
        csv_writer.writerows(rows)
        if f != None:
            f.close()
    else:
        raise Exception('Invalid project_id: ' + project_id)
    
def apply_to_rows(rows, fn):
    for i in range(len(rows)):
        rows[i].append(fn(i+1))
