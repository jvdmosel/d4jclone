from d4jclone.parser.projectParser import parseProject
from d4jclone.util.input_validation import is_valid_pid

def bids(project_id):
    if is_valid_pid(project_id):
        project = parseProject(project_id)
        for i in range(1, project.number_of_bugs+1):
            print(i)
    else:
        raise Exception('Invalid project_id: ' + project_id)
