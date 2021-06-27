from pathlib import Path
from subprocess import PIPE, run
import subprocess
from d4jclone.parser.checkoutParser import parseCheckout
from d4jclone.util.formatting import fill
from d4jclone.core.compile import compile
import xml.etree.ElementTree as ET

def test(workdir = None, relevant = False, single = False, suite = None):
    compile(workdir, 'compile.tests', 'compile-tests')
    workdir = Path(workdir) if workdir != None else Path.cwd()
    checkout = parseCheckout(workdir)
    print(fill('Running ant (test)'), end ='')
    args = ['ant', '-Dbasedir=' + str(workdir), '-Dprojectdir=' + str(checkout.project_dir), '-buildfile', checkout.project.build_file, 'test']
    result = run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if len(result.stderr) != 0:
        print(result.stdout)
        failing_tests = result.stderr
        #print(failing_tests)
        failing_tests = failing_tests.replace('[junit]','')
        failing_tests = failing_tests.replace(' Test ','')
        failing_tests = failing_tests.replace('FAILED','')
        failing_tests = failing_tests.replace(',','')
        failing_tests = failing_tests.replace(' ','').split('\n')
        tree = ET.parse(str(workdir) + '/target/test-reports/' + 'TEST-' + failing_tests[1] + '.xml')
        root = tree.getroot()
        for test in root.findall('testcase'):
            error = test.find('error').text
            if error != None:
                print(test.get('classname') + '::' + test.get('name'))
    else:
        print(result.stdout)
    