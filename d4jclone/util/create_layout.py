import csv
import os
from pathlib import Path

from d4jclone.config import PROJECTDIR
from d4jclone.core.checkout import checkout
from d4jclone.parser.bugParser import parseBug
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.projects import projects

# list of possible layouts for each project
project_layouts = {'Validator': [('src/main/java/', 'src/test/java/'), ('src/share/', 'src/test/')]}

def determineLayout(project_id):
    if project_id in projects.keys():
        project = parseProject(project_id)
        fp = Path(PROJECTDIR) / project_id / 'dir-layout.csv'
        with open(fp, 'w') as csv_file:
            for i in range(1, project.number_of_bugs+1):
                bug = parseBug(project_id, i)
                checkout(project_id, i, 'f', '/home/jvdmosel/workspace/defects/test')
                checkoutdir = '/home/jvdmosel/workspace/defects/test/' + project_id.lower() + '_' + str(i) + '_fixed'
                os.chdir(checkoutdir)
                for layout in project_layouts[project_id]:
                    # a bit greedy, requires only one layout to exist
                    # works for now
                    if (Path(checkoutdir) / layout[0]).is_dir():
                        writer = csv.writer(csv_file)
                        writer.writerow([bug.id, layout[0], layout[1]])
                        break