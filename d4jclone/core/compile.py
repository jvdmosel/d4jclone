import json
from pathlib import Path
from shutil import copyfile, copytree
from subprocess import PIPE, run

from d4jclone.parser.projectParser import parseProject
from d4jclone.parser.bugParser import parseBug
from d4jclone.config import PROJECTDIR
from d4jclone.util.formatting import fill

def compile():
    basedir = Path.cwd()
    parts = basedir.name.split('_')
    # TODO: check if working dir is a possible dir
    project = parseProject(parts[0][:1].upper() + parts[0][1:])
    project_dir = Path(PROJECTDIR) / project.id
    bug = parseBug(project.id, parts[1])
    rev = bug.rev_buggy if parts[2] == 'buggy' else bug.rev_fixed
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
    print(fill('Running ant (compile)'), end ='')
    args = ['ant', '-Dbasedir=' + str(basedir), '-Dprojectdir=' + str(project_dir), '-buildfile', project.build_file, 'compile']
    result = run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if 'BUILD SUCCESSFUL' in result.stdout:
        print('OK')
    else:
        print(rev)
        print(result.stdout, result.stderr)
    