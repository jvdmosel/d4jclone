import re
from pathlib import Path

from d4jclone.config import ENV
from d4jclone.core.checkout import checkout
from d4jclone.core.compile import compile
from d4jclone.core.test import test
from d4jclone.parser.bugParser import getModifiedSources, parseBug
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.input_validation import is_valid_pid

def createRelevantTests(project_id, workdir):
    if is_valid_pid(project_id):
        project = parseProject(project_id)
        for i in range(1, project.number_of_bugs+1):
            bug = parseBug(project_id, i)
            # checkout fixed version
            checkout(project_id, i, 'f', workdir)
            checkout_dir = workdir + '/' + project_id.lower() + '_' + str(i) + '_fixed'
            # compile src
            compile(checkout_dir)
            # compile and run tests
            result = test(checkout_dir, monitor = True)
            pattern = re.compile('[a-zA-Z]*\..*\sfrom')
            # set of loaded classes
            loaded_set = set()
            # set of relevant tests
            relevant_tests = set()
            # modified sources
            modified = getModifiedSources(project_id, bug.id)
            path = Path(ENV['PROJECTDIR']) / project_id / 'relevant_tests'
            if not path.is_dir():
                path.mkdir()
            fp = path / str(bug.id)
            for line in result.stdout.splitlines():
                if 'Testsuite' in line:
                    # a test is relevant if it loads one of the modified sources
                    for item in loaded_set:
                        if item in modified:
                            remove_token = lambda s, token : s.replace(token, '')
                            for token in [' ', '[junit]', 'Testsuite:']:
                                line = remove_token(line, token)
                            relevant_tests.add(line)
                    loaded_set = set()
                elif len(pattern.findall(line)) != 0:
                    s = pattern.findall(line)[0].replace(' from', '')
                    loaded_set.add(s)
            # write tests to file
            with open(fp, 'w') as file:
                for relevant_test in sorted(relevant_tests):
                    file.write(relevant_test + '\n')
