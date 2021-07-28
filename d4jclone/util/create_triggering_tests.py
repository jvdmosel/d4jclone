import xml.etree.ElementTree as ET
from pathlib import Path

from d4jclone.config import PROJECTDIR
from d4jclone.core.checkout import checkout, checkoutVersion
from d4jclone.core.compile import compile
from d4jclone.core.test import test as _test
from d4jclone.core.test import testFails
from d4jclone.parser.bugParser import parseBug
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.projects import projects


def createTriggeringTests(project_id, workdir):
    if project_id in projects.keys():
        project = parseProject(project_id)
        for i in range(1, project.number_of_bugs+1):
            bug = parseBug(project_id, i)
            # checkout fixed version
            checkout(project_id, i, 'b', workdir)
            checkoutdir = workdir + '/' + project_id.lower() + '_' + str(i) + '_buggy'
            checkoutVersion(checkoutdir, 'FIXED')
            # compile src
            compile(checkoutdir)
            # compile and run tests and verify that all tests pass
            result = _test(checkoutdir)
            if len(result.stderr) == 0:
                # checkout buggy version
                checkoutVersion(checkoutdir, 'BUGGY')
                # compile src
                compile(checkoutdir)
                # compile and run tests
                result = _test(checkoutdir)
                # retrieve failing tests
                trigger_tests = []
                to_remove = ['[junit]', 'Test', 'FAILED', ',', '']
                compile_error = False
                for error in result.stderr.split('\n')[:-1]:
                    for token in error.split(' '):
                        if token == 'BUILD':
                            compile_error = True
                        elif token not in to_remove:
                            trigger_tests.append(token)
                # skip if buggy version cannot be compiled
                if compile_error:
                    continue
                # create dir
                path = Path(PROJECTDIR) / project_id / 'trigger_tests'
                if not path.is_dir():
                    path.mkdir()
                fp = path / str(bug.id)
                # determine triggering (bug exposing) testcases
                if len(trigger_tests) > 0:
                    for test in trigger_tests:
                        tree = ET.parse(str(checkoutdir) + '/target/test-reports/' + 'TEST-' + test + '.xml')
                        root = tree.getroot()
                        for test in root.findall('testcase'):
                            fail = test.find('failure')
                            error = test.find('error')
                            message = None
                            if fail != None:
                                message = fail.text
                            elif error != None:
                                message = error.text
                            if message != None:
                                testcase = test.get('classname') + '::' + test.get('name')
                                # run in isolation and verify the testcase fails for the buggy version but not for the fixed version
                                if not testFails(checkoutdir, testcase, 'FIXED') and testFails(checkoutdir, testcase, 'BUGGY'):
                                    with open(fp, 'w') as file:
                                        file.write('--- ' + testcase + '\n')
                                        file.write(message)
