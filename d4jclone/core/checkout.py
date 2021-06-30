import json
import subprocess
from pathlib import Path
from shutil import copyfile, copytree
from subprocess import DEVNULL

from d4jclone.config import PROJECTDIR, REPODIR
from d4jclone.parser.bugParser import parseBug
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.formatting import fill
from d4jclone.util.projects import projects
from git import Repo


def checkout(project_id, bug_id, version, workdir = None):
    if project_id in projects.keys():
        project = parseProject(project_id)
        if 0 < bug_id <= project.number_of_bugs+1:
            bug = parseBug(project_id, bug_id)
            workdir = workdir if workdir != None else '/tmp/'
            if version == 'b':
                tag = 'BUGGY'
            elif version == 'f':
                tag = 'FIXED'
            else:
                raise Exception('Wrong version_id: ' + version)
            checkout = checkoutRevision(project, bug_id, bug.rev_fixed, tag, workdir)
            initLocalRepo(checkout)
            fixBuild(Path(PROJECTDIR) / project.id, checkout, bug, bug.rev_fixed)
            print(fill('Initialize fixed program version'), end ='')
            tagRevision(checkout, project_id, bug_id, 'FIXED')
            applyPatch(checkout, bug)
            print(fill('Initialize buggy program version'), end ='')
            tagRevision(checkout, project_id, bug_id, 'BUGGY')
            tag_name = 'D4JCLONE_' + project.id + '_' + str(bug.id) + '_' + tag
            print(fill('Check out program version: ' + project_id + '-' + str(bug_id) + version), end ='')
            repo = Repo(checkout)
            repo.git.checkout(tag_name)
            print('OK')
        else:
            raise Exception('Error: ' + project_id + '-' + bug_id  + ' is a non-existent bug')
    else:
        raise Exception('Invalid project_id:' + project_id)

def checkoutRevision(project, bug_id, rev, tag, workdir = None): 
    checkout = workdir + '/' + project.id.lower() + '_' + str(bug_id)
    project_repo = Path(REPODIR) / (project.program + '.git')
    checkout = Path(checkout + '_' + tag.lower())
    if checkout.is_dir():
        subprocess.call(['rm', '-f', '-r', checkout])
    repo = Repo.init(project_repo, bare=True).clone(checkout)
    short_sha = repo.git.rev_parse(rev, short=8)
    print(fill('Checking out ' +  short_sha + ' to ' + workdir), end ='')
    repo.git.checkout(rev)
    print('OK')
    return checkout
    
def initLocalRepo(workdir):
    print(fill('Init local repository'), end ='')
    workdir = Path(workdir)
    if workdir.is_dir():
        subprocess.call(['git', '-C', workdir, 'init'], stdout=DEVNULL, stderr=DEVNULL)
        subprocess.call(['git', '-C', workdir, 'config', 'user.name', 'd4jclone'], stdout=DEVNULL, stderr=DEVNULL)
        subprocess.call(['git', '-C', workdir, 'config', 'user.name', 'd4jclone\@localhost'], stdout=DEVNULL, stderr=DEVNULL)
        print('OK')
    else:
        print('FAIL')
        raise Exception('Couldn\'t init local git repository!')
        
def tagRevision(workdir, pid, bid, version):
    tag = 'D4JCLONE_' + pid + '_' + str(bid) + '_' + version
    workdir = Path(workdir)
    if workdir.is_dir():
        with open(workdir / '.d4jclone-config', 'w') as config:
            config.write('#File automatically generated by D4jclone\n')
            config.write('pid=' + pid + '\n')
            config.write('bid=' + str(bid) + '\n')
        subprocess.call(['git', '-C', workdir, 'add', '-A'], stdout=DEVNULL, stderr=DEVNULL)
        subprocess.call(['git', '-C', workdir, 'commit', '-a', '-m', tag], stdout=DEVNULL, stderr=DEVNULL)
        subprocess.call(['git', '-C', workdir, 'tag', tag], stdout=DEVNULL, stderr=DEVNULL)
        print('OK')
    else:
        print('FAIL')
        raise Exception('Couldn\'t tag ' + tag + ' revision!')
        
def applyPatch(workdir, bug):
    print(fill('Apply patch'), end ='')
    workdir = Path(workdir)
    patch = PROJECTDIR + '/' + bug.project + '/patches/' + str(bug.id) + '.src.patch'
    if workdir.is_dir():
        subprocess.call(['git', '-C', workdir, 'apply', patch], stdout=DEVNULL, stderr=DEVNULL)
        print('OK')
    else:
        print('FAIL')

def fixBuild(project_dir, basedir, bug, rev):
    print(fill('Copy generated Ant build file'), end ='')
    if (project_dir / 'project_root.json').is_file():
        with open(project_dir / 'project_root.json') as json_file:
            project_root = json.load(json_file)
            basedir = basedir / project_root[rev]
    if (project_dir / 'alt' / str(bug.id)).is_dir():
        for _file in (project_dir / 'alt' / bug.id).rglob('**/*'):
            if _file.is_file():
                index = _file.parts.index(bug.id) + 1
                copyfile(_file, (project_dir / 'lib').joinpath(*_file.parts[index:]))
    if (project_dir / 'build_files' / rev).is_dir():
        for _file in (project_dir / 'build_files' / rev).glob('*.*'):
            copyfile(_file, basedir / _file.name)
        copytree(project_dir / 'build_files' / rev, basedir, dirs_exist_ok=True)
    print('OK')
