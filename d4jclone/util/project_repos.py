import subprocess
import tarfile
from pathlib import Path

from pycoshark.mongomodels import Project, VCSSystem
from d4jclone.util.projects import projects
from d4jclone.util.db import dbConnect

def createProjectRepos():
    # clean project_repos dir
    path = Path.cwd() / 'project_repos'
    if path.is_dir():
        subprocess.call(['rm', '-r', '-f', path])
    path.mkdir()
    
    dbConnect()
    
    for project in projects.values():        
        internal_id = Project.objects(name=project).only('id').get().id
        repository = VCSSystem.objects(project_id=internal_id).only('repository_file').get().repository_file
    
        if repository.grid_id is None:
            raise Exception('no repository file for project!')

        fname = '{}.tar.gz'.format(project)
        
        archive = path / fname
        repo = path / project
        
        # extract from gridfs
        with open(archive, 'wb') as f:
            f.write(repository.read())

        # get full repository
        with tarfile.open(archive, "r:gz") as tar_gz:
            tar_gz.extractall(path)
            
        # take only .git dir to get bare repo
        with tarfile.open(archive, "w:gz") as tar_gz:
            tar_gz.add(repo / '.git', arcname="")
            
        # extract tarfile
        with tarfile.open(archive, "r:gz") as tar_gz:
            tar_gz.extractall(path / (project + '.git'))

        # remove tarfile and repository
        if archive.is_file():
            archive.unlink()
        if repo.is_dir():
            subprocess.call(['rm', '-r', '-f', repo])
