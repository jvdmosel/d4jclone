from d4jclone.util.formatting import fill
from d4jclone.parser.checkoutParser import parseCheckout
from d4jclone.parser.bugParser import getModifiedSources
from d4jclone.parser.triggerTestParser import parseTriggerTests
from pathlib import Path

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

def export(property, out_file = None, workdir = None):
    if property in properties.keys():
        workdir = Path(workdir) if workdir != None else Path.cwd
        checkout = parseCheckout(workdir)
        if property == 'classes.modified':
            for src in getModifiedSources(checkout.bug):
                print(src)
        elif property == 'classes.relevant':
            pass
        elif property == 'cp.compile':
            pass
        elif property == 'cp.test':
            pass
        elif property == 'dir.bin.classes':
            pass
        elif property == 'dir.bin.tests':
            pass
        elif property == 'dir.src.classes':
            pass
        elif property == 'dir.src.tests':
            pass
        elif property == 'tests.all':
            pass
        elif property == 'tests.relevant':
            pass
        elif property == 'tests.trigger':
            trigger_tests = parseTriggerTests(checkout.project.id, checkout.bug.id)
            if trigger_tests != None:
                for test in trigger_tests.keys():
                    print(test)
    else:
        print('Unknown property ' + property)
        print('usage: d4jclone export -p property_name [-o output_file] [-w work_dir]\n')
        print('Properties:')
        for p in properties.keys():
            print(fill('  ' + p, ' ', 20) + properties[p])