import argparse
import logging
import re
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path
from shutil import copytree

from d4jclone.config import ENV
from d4jclone.core.checkout import checkout
from d4jclone.core.compile import compile
from d4jclone.core.export import parseClasspath, parseProperty
from d4jclone.parser.bugParser import getLoadedClasses
from d4jclone.util.formatting import fill
from d4jclone.util.input_validation import is_valid_pid, is_valid_vid

parser = argparse.ArgumentParser(description='genTests parser')

parser.add_argument(
    '-g',
    default=None,
    metavar='generator',
    type=str,
    required=True,
    help='The test generator to use. \
          Run the following command to see a list of supported test generators: -g help'
)

parser.add_argument(
    '-p',
    default=None,
    metavar='project_id',
    type=str,
    required=True,
    help='Generate tests for this project id.'
)

parser.add_argument(
    '-v',
    default=None,
    metavar='version_id',
    type=str,
    required=True,
    help='Generate tests for this version id.'
)

parser.add_argument(
    '-n',
    default=None,
    metavar='test_id',
    type=int,
    required=True,
    help='The id of the generated test suite (i.e., which run of the same configuration).'
)

parser.add_argument(
    '-o',
    default=None,
    metavar='path',
    type=str,
    required=True,
    help='The root output directory for the generated test suite.'
)

parser.add_argument(
    '-b',
    default=None,
    metavar='seconds',
    type=int,
    required=True,
    help='The total time in seconds allowed for test generation.'
)

parser.add_argument(
    '-c',
    default=None,
    metavar='path',
    type=str,
    required=False,
    help='The file that lists all classes the test generator should target, one class per line (optional).'
)

parser.add_argument(
    '-s',
    default=None,
    metavar='random_seed',
    type=int,
    required=False,
    help='The random seed used for test generation (optional).'
)

parser.add_argument(
    '-t',
    default='/tmp',
    metavar='path',
    type=str,
    required=False,
    help='The temporary root directory to be used to check out the program version (optional).'
)

parser.add_argument(
    '-E',
    default=False,
    action='store_true',
    required=False,
    help='Generate error-revealing (as opposed to regression) tests (optional).'
)

parser.add_argument(
    '-D',
    default=False,
    action='store_true',
    required=False,
    help='Debug: Enable verbose logging and do not delete the temporary check-out directory (optional).'
)

args = parser.parse_args()

# Testsuite generator (randoop or evosuite)
GENERATOR = args.g
# Project id
PID = args.p
# Version id
VID = args.v
# Bug id
BID =  args.v[:-1]
# Id of the generated testsuite
TID = str(args.n)
# Version ('b' or 'f')
VERSION = args.v[-1]
# File that lists all classes the test generator should target
modified = Path(ENV['PROJECTDIR']) / PID / 'modified_classes' / (BID + '.src')
TARGET_CLASSES = args.c if args.c != None else modified
# Directory that contains test generator configuration files
LIBDIR = Path(ENV['BASEDIR']) / 'lib'
# Testgeneration library
TESTGENDIR = LIBDIR / 'testgen'
# Directory of the checked out project version
WORKDIR = Path(args.t) / (PID.lower() + '_' + str(BID) + '_'  + 'buggy' if VERSION == 'b' else 'fixed')
# Temporary directory for testsuite generation
TMPDIR = Path(args.t) / PID / GENERATOR / str(TID)
# Output directory for tar.bz2 testsuite file
OUTDIR = Path(args.o) / PID / GENERATOR / str(TID)
# Total time budget in seconds
TOTAL_BUDGET = args.b
# Set or compute the random seed
SEED = args.n * 1000 + int(BID) if args.s == None else args.s
# Test mode (error-revealing or regression (default))
TEST_MODE = 'error-revealing' if args.E else 'regression'
# Verbose logging
DEBUG = args.D

def logMsgTime(msg):
    # ######  msg: yy-mm-dd hh:mm:ss  ######
    return '######  ' + msg + ': ' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '  ######'
    

def loadConfig():
    config = []
    with open(TESTGENDIR / (GENERATOR + '.config') , 'r') as f:
        for line in f:
            if line.startswith('--'):
                config.append(line.strip())
    return config
    
def getMostCommonPackage():
    with open(TARGET_CLASSES, 'r') as f:
        package_count = {}
        for line in f:
            # removes everything after the package name
            line = re.sub(r'\.[A-Za-z_$][^.]*$', '', line.strip())
            # count the number of times the package occurs within the file
            if line in package_count:
                package_count[line] += 1
            else:
                package_count[line] = 1
        # get package that has the highest count
        # reverse sort first by value (count) then by key (package name)
        package = sorted(package_count.items(), key=lambda x: (x[1],x[0]), reverse=True)[0][0]
        return package
    
def writeTarfile():
    print(fill('Creating test suite archive', '.', 75,), end ='')
    out_file = PID + '-' + VID + '-' + GENERATOR + '.' + TID + '.tar.bz2'
    with tarfile.open(OUTDIR / out_file, 'w:bz2') as tar:
        tar.add(TMPDIR, arcname='.')
    print('OK')
    logging.info('Created test suite archive: ' + str(OUTDIR / out_file))
    # remove tmp dir if debug is not set
    if not DEBUG:
        subprocess.call(['rm', '-f', '-r', TMPDIR.parents[1]])

def generateTestsRandoop(config, classpath, package):
    if TEST_MODE == 'error-revealing':
        config.append('--no-regression-tests=true')
    else:
        config.append('--no-error-revealing-tests=true')
    if DEBUG:
        config.append('--log=' + str(TMPDIR) + '/randoop-log.txt')
        config.append('--selection-log=' + str(TMPDIR) + '/selection-log.txt')
    with open(WORKDIR / 'classes.randoop', 'w') as classes:
        classes.writelines('\n'.join(getLoadedClasses(PID, BID)))
    cmd = ['java -ea -classpath ' + classpath + ':' + str(TESTGENDIR / 'randoop-current.jar'),
           '-Xbootclasspath/a:' + str(TESTGENDIR / 'replacecall-current.jar'),
           '-javaagent:' + str(TESTGENDIR / 'replacecall-current.jar'),
           '-javaagent:' + str(TESTGENDIR / 'covered-class-current.jar'),
           'randoop.main.Main gentests',
           '--classlist=' + str(WORKDIR / 'classes.randoop'),
           '--require-covered-classes=' + str(TARGET_CLASSES),
           '--junit-package-name=' + package,
           '--junit-output-dir=' + str(TMPDIR),
           '--randomseed=' + str(SEED),
           '--time-limit=' + str(TOTAL_BUDGET),
           '--regression-test-basename=RegressionTest',
           '--error-test-basename=ErrorTest']
    cmd += config
    subprocess.run(' '.join(cmd), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
def generateTestsEvosuite(config, classpath):
    if TEST_MODE != 'regression':
        print('Unsupported test mode: ' + TEST_MODE)
        return
    # calculate budget spend per class
    num_classes = sum(1 for line in open(TARGET_CLASSES))
    budget = TOTAL_BUDGET // 2 // num_classes
    classes = []
    with open(TARGET_CLASSES, 'r') as file:
        for line in file:
            classes.append(line.strip())
    for cls in classes:
        cmd = ['java -cp ' + str(TESTGENDIR / 'evosuite-current.jar') + ' org.evosuite.EvoSuite',
               '-class ' + cls,
               '-projectCP ' + classpath,
               '-seed ' + str(SEED),
               '-Dsearch_budget=' + str(budget),
               '-Dassertion_timeout=' + str(budget),
               '-Dtest_dir=' + str(TMPDIR),
               '-Dreport_dir=' + str(OUTDIR / 'statistics' / VID)]
        cmd += config
        subprocess.run(' '.join(cmd), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def generateTests():
    if checkInputs(GENERATOR, PID, VID):
        # Checkout
        checkout(PID, BID, VERSION, workdir=args.t)
        # Compile src and tests
        compile(WORKDIR)
        compile(WORKDIR, 'compile.tests', 'compile-tests')
        # create tmpdir and logdir
        print(fill('Creating temporary output directory', '.', 75,), end ='')
        if not TMPDIR.is_dir():
            TMPDIR.mkdir(parents=True)
        logdir = TMPDIR / 'logs'
        if not logdir.is_dir():
            logdir.mkdir()
        print('OK')
        # set log level to info and only show messages by default
        logging.basicConfig(filename=TMPDIR / 'logs' / (PID + '.' + VID + '.log'), filemode='w', format='%(message)s', level=logging.INFO)
        logging.info(logMsgTime('Start test generation'))
        logging.info('Mode: ' + TEST_MODE)
        logging.info('Parameters:')
        logging.info(' -g ' + GENERATOR)
        logging.info(' -p ' + PID)
        logging.info(' -v ' + VID)
        logging.info(' -n ' + TID)
        logging.info(' -b ' + str(TOTAL_BUDGET))
        logging.info(' -c ' + str(TARGET_CLASSES))
        logging.info(' -s ' + str(SEED))
        config = loadConfig()
        # get full classpath
        classpath = parseClasspath(WORKDIR)
        src, test = parseProperty(PID, BID, VERSION)
        classpath += ':' + str(WORKDIR / src)
        classpath += ':' + str(WORKDIR / test)
        package = getMostCommonPackage()
        print(fill('Generating (' + TEST_MODE + ') tests with: ' + GENERATOR, '.', 75), end ='', flush=True)
        if GENERATOR == 'randoop':
            generateTestsRandoop(config, classpath, package)
        else:
            generateTestsEvosuite(config, classpath)
        # did the generator generate any tests?
        if any(fname.name.endswith('.java') for fname in TMPDIR.glob('**/*')):
            print('OK')
        else:
            print('FAILED')
            print('Test generator (' + GENERATOR + ') did not generate any tests!')
            logging.info('Test generator (' + GENERATOR + ') did not generate any tests!')
            return
        print(fill('Creating output directory', '.', 75,), end ='')
        if not OUTDIR.is_dir():
            OUTDIR.mkdir(parents=True)
        print('OK')
        logging.info('End test generation')
        # copy logs from tmpdir to outdir
        copytree(str(TMPDIR / 'logs'), str(OUTDIR / 'logs'), dirs_exist_ok=True)
        # remove logs from tmpdir
        subprocess.call(['rm', '-f', '-r', TMPDIR / 'logs'])
        # compress resulting tests to tar.bz2
        writeTarfile()

def checkInputs(gen, pid, vid):
    test_generators = ['randoop', 'evosuite']
    if is_valid_pid(pid):
        if is_valid_vid(pid, vid):
            if gen in test_generators:
                return True
            else:
                print('Supported test generators:' + '\n- ' + '\n- '.join(test_generators))
                return False
        else:
            raise Exception('Invalid version_id: ' + vid)
    else:
        raise Exception('Invalid project_id: ' + pid)
  
generateTests()
