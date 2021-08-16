import xml.etree.ElementTree as ET
from pathlib import Path

from d4jclone.config import ENV
from d4jclone.core.checkout import checkout, checkoutVersion
from d4jclone.core.compile import compile
from d4jclone.core.test import test as _test
from d4jclone.core.test import testFails
from d4jclone.parser.bugParser import parseBug
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.input_validation import is_valid_pid

def createTriggeringTests(project_id, workdir):
    if is_valid_pid(project_id):
        project = parseProject(project_id)
        for i in range(1, project.number_of_bugs+1):
            bug = parseBug(project_id, i)
            # checkout fixed version
            checkout(project_id, i, 'b', workdir)
            checkout_dir = workdir + '/' + project_id.lower() + '_' + str(i) + '_buggy'
            checkoutVersion(checkout_dir, 'FIXED')
            # compile src
            compile(checkout_dir)
            # compile and run tests and verify that all tests pass
            result = _test(checkout_dir)
            if len(result.stderr) == 0:
                # checkout buggy version
                checkoutVersion(checkout_dir, 'BUGGY')
                # compile src
                compile(checkout_dir)
                # compile and run tests
                result = _test(checkout_dir)
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
                path = Path(ENV['PROJECTDIR']) / project_id / 'trigger_tests'
                if not path.is_dir():
                    path.mkdir()
                fp = path / str(bug.id)
                # determine triggering (bug exposing) testcases
                if len(trigger_tests) > 0:
                    for test in trigger_tests:
                        tree = ET.parse(str(checkout_dir) + '/target/test-reports/' + 'TEST-' + test + '.xml')
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
                                if not testFails(checkout_dir, testcase, 'FIXED') and testFails(checkout_dir, testcase, 'BUGGY'):
                                    with open(fp, 'w') as file:
                                        file.write('--- ' + testcase + '\n')
                                        file.write(message)
