import csv
import os
import subprocess
from pathlib import Path

from d4jclone.config import BASEDIR, PROJECTDIR
from d4jclone.core.checkout import checkout
from d4jclone.parser.bugParser import getModifiedSources, parseBug
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.projects import projects

def determineLayout(project_id, bug_id):
    with open(PROJECTDIR + '/' + project_id + '/dir-layout.csv', 'r') as layout_file:
        csv_reader = csv.reader(layout_file)
        # filters csv file for row of unique bug id
        layout = next(filter(lambda x: str(bug_id) in x, csv_reader))
        return (layout[1],layout[2])

def createPatches(project_id):
    if project_id in projects.keys():
        project = parseProject(project_id)
        for i in range(1, project.number_of_bugs+1):
            bug = parseBug(project_id, i)
            checkout(project_id, i, 'f', BASEDIR + '/test')
            checkoutdir =  BASEDIR + '/test/' + project_id.lower() + '_' + str(i) + '_fixed'
            outsrc = PROJECTDIR + '/' + project_id + '/patches/' + str(i) + '.src.patch'
            outtest = PROJECTDIR + '/' + project_id + '/patches/' + str(i) + '.test.patch'
            cwd = Path.cwd()
            os.chdir(checkoutdir)
            modified = getModifiedSources(bug)
            testfiles = []
            srcfiles = []
            layout = determineLayout(project_id, bug.id)
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
