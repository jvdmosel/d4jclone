import json
from pathlib import Path
from shutil import copyfile, copytree
from subprocess import PIPE, run

from d4jclone.parser.checkoutParser import parseCheckout
from d4jclone.util.formatting import fill

def fixBuild(project_dir, basedir, bug, rev):
    if (project_dir / 'project_root.json').is_file():
        with open(project_dir / 'project_root.json') as json_file:
            project_root = json.load(json_file)
            basedir = basedir / project_root[rev]
    if (project_dir / 'alt' / bug.id).is_dir():
        for _file in (project_dir / 'alt' / bug.id).rglob('**/*'):
            if _file.is_file():
                index = _file.parts.index(bug.id) + 1
                copyfile(_file, (project_dir / 'lib').joinpath(*_file.parts[index:]))
    if (project_dir / 'build_files' / rev).is_dir():
        for _file in (project_dir / 'build_files' / rev).glob('*.*'):
            copyfile(_file, basedir / _file.name)
        copytree(project_dir / 'build_files' / rev, basedir, dirs_exist_ok=True)

def compile(workdir = None, task = 'compile', arg = 'compile'):
    workdir = Path(workdir) if workdir != None else Path.cwd
    checkout = parseCheckout(workdir)
    fixBuild(checkout.project_dir, workdir, checkout.bug, checkout.rev)
    print(fill('Running ant (' + task + ')'), end ='')
    args = ['ant', '-Dbasedir=' + str(workdir), '-Dprojectdir=' + str(checkout.project_dir), '-buildfile', checkout.project.build_file, arg]
    result = run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if 'BUILD SUCCESSFUL' in result.stdout:
        print('OK')
    else:
        print(checkout.rev)
        print(result.stdout, result.stderr)