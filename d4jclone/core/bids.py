from d4jclone.util.projects import projects
from d4jclone.parser.projectParser import parseProject

def bids(project_id):
    if project_id in projects.keys():
        project = parseProject(project_id)
        for i in range(1, project.number_of_bugs+1):
            print(i)
    else:
        raise Exception('Invalid project_id: ' + project_id)