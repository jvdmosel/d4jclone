import re
from pathlib import Path

from d4jclone.config import ENV
from d4jclone.core.checkout import checkout
from d4jclone.core.compile import compile
from d4jclone.core.test import test
from d4jclone.parser.bugParser import getLayout, parseBug
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.projects import projects

def getClasses(workdir, layout):
    target_dir = Path(workdir) / layout 
    java_files = [str(x) for x in target_dir.glob('**/*.java')]
    # remove everything before the package name
    classes =  [file[file.find(layout)+len(layout):] for file in java_files]
    # replace slashes with dots and remove .java postfix
    classes = [cls.replace('/', '.')[1:-5] for cls in classes]    
    return classes

def createLoadedClasses(project_id, workdir):
    if project_id in projects.keys():
        project = parseProject(project_id)
        for i in range(1, project.number_of_bugs+1):
            bug = parseBug(project_id, i)
            # checkout fixed version
            checkout(project_id, i, 'f', workdir)
            checkout_dir = workdir + '/' + project_id.lower() + '_' + str(i) + '_fixed'
            # compile src
            compile(checkout_dir)
            # compile and run tests
            result = test(checkout_dir, relevant=True, monitor = True)
            # pattern for finding classes in result
            pattern = re.compile('[a-zA-Z]*\..*\sfrom')
            # get lists of src and test classes
            src_dir, test_dir = getLayout(bug, 'f')
            src_classes = getClasses(checkout_dir, src_dir)
            test_classes = getClasses(checkout_dir, test_dir)
            # set of loaded src classes
            src_loaded_set = set()
            test_loaded_set = set()
            path = Path(ENV['PROJECTDIR']) / project_id / 'loaded_classes'
            if not path.is_dir():
                path.mkdir()
            src_fp = path / (str(bug.id) + '.src')
            test_fp = path / (str(bug.id) + '.test')
            for line in result.stdout.splitlines():
                if len(pattern.findall(line)) != 0:
                    s = pattern.findall(line)[0].replace(' from', '')
                    if s in src_classes:
                        src_loaded_set.add(s)
                    elif s in test_classes:
                        test_loaded_set.add(s)
            with open(src_fp, 'w') as src_file:
                src_file.write('\n'.join(sorted(src_loaded_set)))
            with open(test_fp, 'w') as test_file:
                test_file.write('\n'.join(sorted(test_loaded_set)))
