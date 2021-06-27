from d4jclone.parser.projectParser import parseProject
from d4jclone.parser.bugParser import parseBug
from pathlib import Path
from d4jclone.config import PROJECTDIR

class Checkout():
    def __init__(self, project, project_dir, bug, rev):
        self.project = project
        self.project_dir = project_dir
        self.bug = bug
        self.rev = rev

def parseCheckout(dir):
    parts = dir.name.split('_')
    # TODO: check if working dir is a possible dir
    project = parseProject(parts[0][:1].upper() + parts[0][1:])
    project_dir = Path(PROJECTDIR) / project.id
    bug = parseBug(project.id, parts[1])
    rev = bug.rev_buggy if parts[2] == 'buggy' else bug.rev_fixed
    return Checkout(project, project_dir, bug, rev)