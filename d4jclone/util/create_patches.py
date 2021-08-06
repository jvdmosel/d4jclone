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
            checkoutdir =  ENV['BASEDIR'] + '/test/' + project_id.lower() + '_' + str(i) + '_fixed'
            outsrc = ENV['PROJECTDIR'] + '/' + project_id + '/patches/' + str(i) + '.src.patch'
            outtest = ENV['PROJECTDIR'] + '/' + project_id + '/patches/' + str(i) + '.test.patch'
            cwd = Path.cwd()
            os.chdir(checkoutdir)
            modified = getModifiedSources(bug)
            testfiles = []
            srcfiles = []
            layout = getLayout(bug)
            for src in modified:
                if 'Test' in src:
                    s = layout[1] + src.replace('.', '/') + '.java'
                    testfiles.append(s)
                else:
                    s = layout[0] + src.replace('.', '/') + '.java'
                    srcfiles.append(s)
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
