import json
import subprocess
from pathlib import Path
from shutil import copyfile, copytree
from subprocess import DEVNULL

from d4jclone.config import ENV
from d4jclone.parser.bugParser import parseBug
from d4jclone.parser.checkoutParser import parseCheckout
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.formatting import fill
from d4jclone.util.input_validation import is_valid_pid, is_valid_bid
from git import Repo


def checkout(project_id, bug_id, version, workdir = None):
    """ Checkout a particular project version.

    Args:
        project_id (str): The id of the project for which a particular version shall be checked out.
        bug_id (int): The id of the bug that shall be checked out.
        version (str): The version that shall be checked out ('b' or 'f')
        workdir (str, optional): The working directory to which the buggy or fixed project version shall be checked out. Defaults to None.

    Raises:
        Exception: Wrong version ID exception
        Exception: Non-existent bug exception
        Exception: Invalid project ID exception
    """
    
    if is_valid_pid(project_id):
        project = parseProject(project_id)
        if is_valid_bid(project_id, bug_id):
            bug = parseBug(project_id, bug_id)
            workdir = workdir if workdir != None else '/tmp/'
            if version == 'b':
                tag = 'BUGGY'
            elif version == 'f':
                tag = 'FIXED'
            else:
                raise Exception('Wrong version_id: ' + version)
            # checkout the fixed revision id
            checkout = checkoutRevision(project, bug_id, bug.rev_fixed, tag, workdir)
            initLocalRepo(checkout)
            print(fill('Tag post-fix revision', '.', 75), end ='')
            tagRevision(checkout, project_id, bug_id, 'POST_FIX')
            # copy build files to checked out dir
            fixBuild(project.id, checkout, bug, bug.rev_fixed)
            print(fill('Initialize fixed program version', '.', 75), end ='')
            tagRevision(checkout, project_id, bug_id, 'FIXED')
            # apply patch to obtain the buggy version
            applyPatch(checkout, bug)
            print(fill('Initialize buggy program version', '.', 75), end ='')
            tagRevision(checkout, project_id, bug_id, 'BUGGY')
            repo = Repo(checkout)
            print(fill('Tag pre-fix revision', '.', 75), end ='')
            # checkout postfix revision and apply unmodified patch to obtain prefix revision
            repo.git.checkout('D4JCLONE_' + project.id + '_' + str(bug.id) + '_POST_FIX')
            subprocess.call('git -C ' + str(checkout) + ' diff ' + bug.rev_fixed + ' ' + bug.rev_buggy + ' > ' + str(checkout) + '/tmp.patch', shell=True)
            subprocess.call(['git', '-C', checkout, 'apply', str(checkout) + '/tmp.patch'], stdout=DEVNULL, stderr=DEVNULL)
            subprocess.call(['rm', '-f', str(checkout) + '/tmp.patch'])
            tagRevision(checkout, project_id, bug_id, 'PRE_FIX')
            # checkout the requested program version
            tag_name = 'D4JCLONE_' + project.id + '_' + str(bug.id) + '_' + tag
            print(fill('Check out program version: ' + project_id + '-' + str(bug_id) + version, '.', 75), end ='', flush=True)
            repo.git.checkout(tag_name)
            print('OK')
        else:
            raise Exception('Error: ' + project_id + '-' + bug_id  + ' is a non-existent bug')
    else:
        raise Exception('Invalid project_id: ' + project_id)

def checkoutRevision(project, bug_id, rev, tag, workdir):
    """ Checkout a project revision to a given directory

    Args:
        project (Project): The project object (bugParser)
        bug_id (int): The bug ID
        rev (str): The revision to be checked out
        tag (str): The tag
        workdir (str): The working directory

    Returns:
        [Path]: Path to the checked out revision directory
    """
    # clone the repository to workdir/projectID_bugID_tag
    checkout = workdir + '/' + project.id.lower() + '_' + str(bug_id)
    project_repo = Path(ENV['REPODIR']) / (project.program + '.git')
    checkout = Path(checkout + '_' + tag.lower())
    # remove if exists
    if checkout.is_dir():
        subprocess.call(['rm', '-f', '-r', checkout])
    repo = Repo.init(project_repo, bare=True).clone(checkout)
    short_sha = repo.git.rev_parse(rev, short=8)
    # checkout the revision
    print(fill('Checking out ' +  short_sha + ' to ' + workdir, '.', 75), end ='')
    repo.git.checkout(rev)
    print('OK')
    return checkout

def checkoutVersion(workdir, version):
    """ Check out a version (BUGGY / FIXED) for a given checked out directory
       Helper function for core.test and util.create_triggering_tests

    Args:
        workdir (str): Path to the directory of the checked out bug
        version (str): Version to be checked out

    Raises:
        Exception: Could not find directory

    Returns:
        [bool]: True if checkout was successful
    """
    path = Path(workdir)
    if path.is_dir():
        checkout = parseCheckout(path)
        tag = 'D4JCLONE_' + checkout.project.id + '_' + str(checkout.bug.id) + '_' + version
        result = subprocess.call(['git', '-C', path, 'checkout', tag])
    else:
        raise Exception('Couldn\'t find directory!')
    return bool(result)
    
def initLocalRepo(workdir):
    """ Initialize a local repository in the given working directory 

    Args:
        workdir (str): The working directory

    Raises:
        Exception: Could not initialize local repository
    """
    
    print(fill('Init local repository', '.', 75), end ='')
    workdir = Path(workdir)
    if workdir.is_dir():
        subprocess.call(['git', '-C', workdir, 'init'], stdout=DEVNULL, stderr=DEVNULL)
        subprocess.call(['git', '-C', workdir, 'config', 'user.name', 'd4jclone'], stdout=DEVNULL, stderr=DEVNULL)
        subprocess.call(['git', '-C', workdir, 'config', 'user.name', 'd4jclone\@localhost'], stdout=DEVNULL, stderr=DEVNULL)
        print('OK')
    else:
        print('FAILED')
        raise Exception('Couldn\'t init local git repository!')
        
def tagRevision(workdir, pid, bid, version):
    """ Tags a revision with a given version tag

    Args:
        workdir (str): The working directory
        pid (str): The project id
        bid (int): The bug id
        version (str): The version tag

    Raises:
        Exception: Could not tag revision
    """
    
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
        print('FAILED')
        raise Exception('Couldn\'t tag ' + tag + ' revision!')
        
def applyPatch(workdir, bug, patch = None):
    """ By default applies the reverse bugfix for a given bug (fixed -> buggy).
        If a patch is provided applies the given patch instead.

    Args:
        workdir (str): The working directory
        bug (Bug): The bug 
        patch (str, optional): Path to the patch file. Defaults to None.
    """
    
    print(fill('Apply patch', '.', 75), end ='')
    workdir = Path(workdir)
    if patch == None:
        patch = ENV['PROJECTDIR'] + '/' + bug.project + '/patches/' + str(bug.id) + '.src.patch'
    if workdir.is_dir():
        subprocess.call(['git', '-C', workdir, 'apply', patch], stdout=DEVNULL, stderr=DEVNULL)
        print('OK')
    else:
        print('FAILED')

def fixBuild(project_id, workdir, bug, rev):
    """ Fixes the build by copying the relevant d4jclone build files for a given revision 

    Args:
        project_id (str): The project ID
        workdir (str): The working directory
        bug (Bug): The bug
        rev (str): The revision
    """
    
    project_dir = Path(ENV['PROJECTDIR']) / project_id
    print(fill('Copy generated Ant build file', '.', 75), end ='')
    # some projects have a different project root directory
    if (project_dir / 'project_root.json').is_file():
        with open(project_dir / 'project_root.json') as json_file:
            project_root = json.load(json_file)
            workdir = workdir / project_root[rev]
    # some projects have multi-module builds
    if (project_dir / 'alt' / str(bug.id)).is_dir():
        for _file in (project_dir / 'alt' / bug.id).rglob('**/*'):
            if _file.is_file():
                index = _file.parts.index(bug.id) + 1
                copyfile(_file, (project_dir / 'lib').joinpath(*_file.parts[index:]))
    # copy the build files for the given revision
    if (project_dir / 'build_files' / rev).is_dir():
        for _file in (project_dir / 'build_files' / rev).glob('*.*'):
            copyfile(_file, workdir / _file.name)
        copytree(project_dir / 'build_files' / rev, workdir, dirs_exist_ok=True)
    print('OK')
