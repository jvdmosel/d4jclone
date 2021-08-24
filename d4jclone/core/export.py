import sys
from pathlib import Path
from subprocess import PIPE, run

from d4jclone.config import ENV
from d4jclone.parser.bugParser import (getLayout, getLoadedClasses,
                                       getModifiedSources, getRelevantTests,
                                       getTriggerTests, parseBug)
from d4jclone.parser.checkoutParser import getClasses
from d4jclone.parser.checkoutParser import parseCheckout
from d4jclone.util.formatting import fill
from d4jclone.util.input_validation import is_valid_pid

properties = {
    'classes.modified': 'Classes modified by the bug fix',
    'classes.relevant': 'Classes loaded by the triggering tests',
    'cp.compile': 'Classpath to compile the project',
    'cp.test': 'Classpath to compile and run the developer-written tests',
    'dir.bin.classes': 'Target directory of classes',
    'dir.bin.tests': 'Target directory of test classes',
    'dir.src.classes': 'Source directory of classes',
    'dir.src.tests': 'Source directory of tests',
    'tests.all': 'List of all developer-written tests',
    'tests.relevant': 'Relevant tests that touch at least one of the modified sources',
    'tests.trigger': 'Trigger tests that expose the bug',    
}

def export(property, file = None, workdir = None):
    if property in properties.keys():
        f = None
        if file != None:
            f = open(file, 'w')
            # print() now prints to file instead of stdout
            sys.stdout = f
        workdir = Path(workdir) if workdir != None else Path.cwd()
        checkout = parseCheckout(workdir)
        # Classes modified by the bug fix
        if property == 'classes.modified':
            for src in getModifiedSources(checkout.project.id, checkout.bug.id):
                print(src)
        # Classes loaded by the triggering tests
        elif property == 'classes.relevant':
            for src in getLoadedClasses(checkout.project, checkout.bug):
                print(src)
        # Classpath to compile the project
        elif property == 'cp.compile':
            print(parseClasspath(workdir))
        # Classpath to compile and run the developer-written tests
        elif property == 'cp.test':
            print(parseClasspath(workdir, 'test.classpath'))
        # Target directory of classes and test classes
        elif property == 'dir.bin.classes' or property == 'dir.bin.tests':
            src, test = parseProperty(checkout.project.id, checkout.bug.id, 'b')
            print(src if property == 'dir.bin.classes' else test)
        # Source directory of classes and tests
        elif property == 'dir.src.classes' or property == 'dir.src.tests':
            src, test = getLayout(checkout.bug, 'b')
            print(src if property == 'dir.src.classes' else test)
        # List of all developer-written tests
        elif property == 'tests.all':
            for test in sorted(getClasses(workdir, getLayout(checkout.bug, 'b')[1])):
                print(test)
        # Relevant tests that touch at least one of the modified sources
        elif property == 'tests.relevant':
            for test in getRelevantTests(checkout.project.id, checkout.bug.id):
                print(test)
        # Trigger tests that expose the bug
        elif property == 'tests.trigger':
            trigger_tests = getTriggerTests(checkout.project.id, checkout.bug.id)
            if trigger_tests != None:
                for test in trigger_tests.keys():
                    print(test)
        if f != None:
            f.close()
    else:
        print('Unknown property ' + property)
        print('usage: d4jclone export -p property_name [-o output_file] [-w work_dir]\n')
        print('Properties:')
        for p in properties.keys():
            print(fill('  ' + p, ' ', 20) + properties[p])

def parseProperty(project_id, bug_id, version):
    if is_valid_pid(project_id):
        bug = parseBug(project_id, bug_id)
        rev = bug.rev_buggy if version == 'b' else bug.rev_fixed
        path = Path(ENV['PROJECTDIR']) / project_id / 'build_files' / rev / 'maven-build.properties'
        with open(path, 'r') as properties:
            dirs = {'maven.build.dir=': None,
                    'maven.build.outputDir=': None,
                    'maven.build.testOutputDir=': None}
            for line in properties:
                for key in dirs.keys():
                    if line.startswith(key):
                        dirs[key] = line[len(key):].strip()
            prefix = dirs['maven.build.dir=']
            output_dir = dirs['maven.build.outputDir='].replace('${maven.build.dir}', prefix)
            test_dir = dirs['maven.build.testOutputDir='].replace('${maven.build.dir}', prefix)
            return (output_dir, test_dir)
    else:
        raise Exception('Invalid project_id: ' + project_id)

def parseClasspath(workdir, arg = 'classpath'):
    checkout = parseCheckout(workdir)
    args = ['ant', 
            '-Dbasedir=' + str(workdir), 
            '-Dprojectdir=' + str(checkout.project_dir), 
            '-buildfile', checkout.project.build_file, 
            'print-' + arg]
    result = run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    for line in result.stdout.split('\n'):
        line = line.strip()
        if line.startswith('[echo] '):
            return line[len('[echo] '):]
