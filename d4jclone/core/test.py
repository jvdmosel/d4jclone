import re
import subprocess
from pathlib import Path
from subprocess import PIPE, run

from d4jclone.config import ENV
from d4jclone.core.checkout import checkoutVersion
from d4jclone.core.compile import compile
from d4jclone.parser.checkoutParser import parseCheckout
from d4jclone.util.formatting import fill

class_method = re.compile('([^:]+::[^:]+)')

def test(workdir = None, testcase = None, relevant = False, testsuite = None, monitor = False):
    """Runs tests on a checked-out project version.

    Args:
        workdir (str, optional): The working directory of the checked-out project version. Defaults to the current working directory.
        testcase ([str, optional): Name of the single testcase that should be run. Defaults to all developer written tests.
        relevant (bool, optional): Whether only the relevant tests should be run. Defaults to False.
        testsuite (str, optional): The path to an external testsuite. Defaults to None.
        monitor (bool, optional): Whether the class loader should be monitored. Defaults to False.

    Returns:
        (str,str): The output (stdout, stderr).
    """
    
    workdir = Path(workdir) if workdir != None else Path.cwd()
    testdir = workdir / '.test_suite'
    if testsuite:
        extractTestsuite(testsuite, testdir)
        compile(workdir, 'compile.gen.tests', 'compile-gen-tests', testdir)
    else:
        compile(workdir, 'compile.tests', 'compile-tests')
    checkout = parseCheckout(workdir)
    args = ['ant', 
            '-Dbasedir=' + str(workdir), 
            '-Dprojectdir=' + str(checkout.project_dir),
            '-Dlibdir=' + ENV['LIBDIR']]
    if testcase != None and bool(class_method.match(testcase)):
        args.extend(['-Dtest.entry.class=' + testcase.split('::')[0], 
                     '-Dtest.entry.method=' + testcase.split('::')[1]])
    elif relevant:
        args.extend(['-Dtest.relevant=' + str(checkout.project_dir) + '/relevant_tests/' + str(checkout.bug.id)])
    if monitor:
        args.extend(['-Dtest.monitor=True'])
    print(fill('Running ant (test)', '.', 75), end ='')
    if testsuite:
        args.extend(['-Dtest.dir=' + str(testdir), '-buildfile', checkout.project.build_file, 'run-gen-tests'])
    else:
        args.extend(['-buildfile', checkout.project.build_file, 'test'])
    result = run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print('OK')
    return result

def testFails(workdir, testcase, version):
    """Performs a checkout for a given version, runs the testcase and checks whether it fails.

    Args:
        workdir (str): The working directory of the checked-out project version.
        testcase (str): The testcase that should be run.
        version (str): The version that should be checked out.

    Raises:
        Exception: Directory not found exception

    Returns:
        bool: True if the testcase fails, otherwise False
    """
    workdir = Path(workdir)
    if workdir.is_dir():
        checkoutVersion(workdir, version)
        compile(workdir)
        result = test(workdir, testcase)
        return True if len(result.stderr) > 0 else False
    else:
        raise Exception('Couldn\'t find directory!')
    
def extractTestsuite(testsuite, testdir):
    """Extracts a given external testsuite archive (tar.bz2) to the testdir.

    Args:
        testsuite (str): Path to the testsuite archive.
        testdir (str): Path to the test directory.
    """
    if not Path(testsuite).is_file():
        print('Test suite archive not found: ' + testsuite)
        return
    path = Path(testdir)
    if not path.is_dir():
        path.mkdir()
    else:
        subprocess.call(['rm', '-f', '-r', str(path) + '/*'])
    subprocess.call(['tar', '-xjf', testsuite, '-C', testdir])
