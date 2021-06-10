from pathlib import Path
import subprocess
from git import Repo
from d4jclone.parser.bugParser import parseBug
from d4jclone.util.projects import projects
from d4jclone.parser.projectParser import parseProject
from d4jclone.config import REPODIR
from d4jclone.util.formatting import fill

def checkout(project_id, bug_id, version, workdir = None):
    if project_id in projects.keys():
        project = parseProject(project_id)
        if 0 < bug_id <= project.number_of_bugs+1:
            bug = parseBug(project_id, bug_id)
            workdir = workdir if workdir != None else '/tmp/'
            checkout = workdir + '/' + project.id.lower() + '_' + str(bug_id)
            project_repo = Path(REPODIR) / (project.program + '.git')
            if version == 'b':
                version = 'BUGGY_VERSION'
                checkout = Path(checkout + '_buggy')
            elif version == 'f':
                version = 'FIXED_VERSION'
                checkout = Path(checkout + '_fixed')
            else:
                raise Exception('Wrong version_id: ' + version)
            if checkout.is_dir():
                subprocess.call(['rm', '-f', '-r', checkout])
            repo = Repo.init(project_repo, bare=True).clone(checkout)
            short_sha = repo.git.rev_parse(bug.rev_buggy, short=8)
            if version == 'FIXED_VERSION':
                short_sha = repo.git.rev_parse(bug.rev_fixed, short=8)
            print(fill('Checking out ' +  short_sha + ' to ' + workdir), end ='')
            repo.git.checkout(bug.rev_fixed, '-b', 'D4jclone_' + project.id + '_' + str(bug_id) + '_' + version)
            print('OK')
        else:
            raise Exception('Error: ' + project_id + '-' + bug_id  + ' is a non-existent bug')
    else:
        raise Exception('Invalid project_id:' + project_id)