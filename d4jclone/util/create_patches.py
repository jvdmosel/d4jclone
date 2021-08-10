import os
import subprocess
from pathlib import Path

from d4jclone.config import ENV
from d4jclone.core.checkout import checkout
from d4jclone.parser.bugParser import getLayout, getModifiedSources, parseBug
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.projects import projects

def createPatches(project_id):
    if project_id in projects.keys():
        project = parseProject(project_id)
        for i in range(1, project.number_of_bugs+1):
            bug = parseBug(project_id, i)
            checkout(project_id, i, 'f', ENV['BASEDIR'] + '/test')
            checkout_dir =  ENV['BASEDIR'] + '/test/' + project_id.lower() + '_' + str(i) + '_fixed'
            path = Path(ENV['PROJECTDIR']) / project_id / 'patches'
            if not path.is_dir():
                path.mkdir()
            outsrc = path / (str(i) + '.src.patch')
            outtest = path / (str(i) + '.test.patch')
            cwd = Path.cwd()
            os.chdir(checkout_dir)
            modified = getModifiedSources(bug)
            testfiles = []
            srcfiles = []
            layout = getLayout(bug, 'f')
            for src in modified:
                src_path = Path(checkout_dir) / layout[0] / (src.replace('.', '/') + '.java')
                test_path = Path(checkout_dir) / layout[1] / (src.replace('.', '/') + '.java')
                if src_path.is_file():
                    srcfiles.append(str(src_path))
                elif test_path.is_file():
                    testfiles.append(str(test_path))
                else:
                    raise Exception(src + ' does not exist in ' + checkout_dir)
            if len(testfiles) > 0:
                f = open(outtest, 'w')
                for file in testfiles:
                    subprocess.call(['git', 'diff', bug.rev_fixed, bug.rev_buggy, file], stdout=f)
                f.close()
            if len(srcfiles) > 0:
                f = open(outsrc, 'w')
                for file in srcfiles:
                    subprocess.call(['git', 'diff', bug.rev_fixed, bug.rev_buggy, file], stdout=f)
                f.close()
            os.chdir(cwd)
