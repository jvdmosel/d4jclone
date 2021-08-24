from d4jclone.parser.projectParser import parseProject
from d4jclone.parser.bugParser import parseBug
from pathlib import Path
from d4jclone.config import ENV

class Checkout():
    def __init__(self, project, project_dir, bug, rev, version):
        self.project = project
        self.project_dir = project_dir
        self.bug = bug
        self.rev = rev
        self.version = version

def parseCheckout(dir):
    parts = dir.name.split('_')
    # TODO: check if working dir is a possible dir
    project = parseProject(parts[0][:1].upper() + parts[0][1:])
    project_dir = Path(ENV['PROJECTDIR']) / project.id
    bug = parseBug(project.id, parts[1])
    rev = bug.rev_buggy if parts[2] == 'buggy' else bug.rev_fixed
    version = "BUGGY" if parts[2] == 'buggy' else "FIXED"
    return Checkout(project, project_dir, bug, rev, version)

def getClasses(workdir, layout):
    target_dir = Path(workdir) / layout 
    java_files = [str(x) for x in target_dir.glob('**/*.java')]
    # remove everything before the package name
    classes =  [file[file.find(layout)+len(layout):] for file in java_files]
    # replace slashes with dots and remove .java postfix
    classes = [cls.replace('/', '.')[1:-5] for cls in classes]    
    return classes