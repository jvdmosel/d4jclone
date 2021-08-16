import csv
from pathlib import Path

from d4jclone.config import ENV
from d4jclone.core.checkout import checkout
from d4jclone.parser.bugParser import parseBug
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.input_validation import is_valid_pid

# list of possible layouts for each project
project_layouts = {'Validator': [('src/main/java', 'src/test/java'), ('src/share', 'src/test')]}

def findLayout(checkout_dir, project_id):
    # greedy approach, works for now
    for layout in project_layouts[project_id]:
        if (Path(checkout_dir) / layout[0]).is_dir():
            return layout

def createLayout(project_id):
    if is_valid_pid(project_id):
        project = parseProject(project_id)
        fp = Path(ENV['PROJECTDIR']) / project_id / 'dir-layout.csv'
        with open(fp, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for i in range(1, project.number_of_bugs+1):
                bug = parseBug(project_id, i)
                # write layout for fixed version
                checkout(project_id, i, 'b', ENV['BASEDIR'] + '/test')
                checkout_dir = ENV['BASEDIR'] + '/test/' + project_id.lower() + '_' + str(i) + '_buggy'
                buggy_layout = findLayout(checkout_dir, project_id)
                writer.writerow([bug.rev_buggy, buggy_layout[0], buggy_layout[1]])
                # write layout for buggy version
                checkout(project_id, i, 'f', ENV['BASEDIR'] + '/test')
                checkout_dir = ENV['BASEDIR'] + '/test/' + project_id.lower() + '_' + str(i) + '_fixed'
                fixed_layout = findLayout(checkout_dir, project_id)
                writer.writerow([bug.rev_fixed, fixed_layout[0], fixed_layout[1]])
