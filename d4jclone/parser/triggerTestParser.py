from pathlib import Path
from d4jclone.config import ENV

def parseTriggerTests(project_id, bug_id):
    file_path = Path(ENV['PROJECTDIR']) / project_id / 'trigger_tests' / str(bug_id)
    # check if there are any triggering tests for this bug
    if file_path.is_file():
        with open(file_path, 'r') as file:
            testcase = ''
            trigger_tests = {}
            # we only care for testcases and root causes
            for line in file:
                # testcases are prefixed with ---
                if line[:3] == '---':
                    testcase = line[4:].strip('\n')
                    trigger_tests[testcase] = []
                # stacktrace is prefixed with \t (skip)
                elif line[0] == '\t':
                    continue
                # root cause
                else:
                    trigger_tests[testcase].append(line.strip('\n'))
        return trigger_tests
    else:
        return None