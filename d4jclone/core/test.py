import re
from pathlib import Path
from subprocess import PIPE, run

from d4jclone.core.checkout import checkoutVersion
from d4jclone.core.compile import compile
from d4jclone.parser.checkoutParser import parseCheckout
from d4jclone.util.formatting import fill

class_method = re.compile('([^:]+::[^:]+)')

def test(workdir = None, testcase = None, relevant = False, suite = None, monitor = False): 
    workdir = Path(workdir) if workdir != None else Path.cwd()
    compile(workdir, 'compile.tests', 'compile-tests')
    checkout = parseCheckout(workdir)
    args = ['ant', 
            '-Dbasedir=' + str(workdir), 
            '-Dprojectdir=' + str(checkout.project_dir)]
    if testcase != None and bool(class_method.match(testcase)):
        args.extend(['-Dtest.entry.class=' + testcase.split('::')[0], 
                     '-Dtest.entry.method=' + testcase.split('::')[1]])
    elif relevant:
        args.extend(['-Dtest.relevant=' + str(checkout.project_dir) + '/relevant_tests/' + str(checkout.bug.id)])
    if monitor:
        args.extend(['-Dtest.monitor=True'])
    print(fill('Running ant (test)'), end ='')
    args.extend(['-buildfile', checkout.project.build_file, 'test'])
    result = run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print('OK')
    return result

def testFails(workdir, testcase, version):
    workdir = Path(workdir)
    if workdir.is_dir():
        checkoutVersion(workdir, version)
        compile(workdir)
        result = test(workdir, testcase)
        return True if len(result.stderr) > 0 else False
    else:
        raise Exception('Couldn\'t find directory!')
