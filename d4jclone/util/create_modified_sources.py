from pathlib import Path

from d4jclone.util.db import dbConnect
from d4jclone.config import ENV
from d4jclone.parser.bugParser import parseBug
from d4jclone.util.projects import projects
from pycoshark.mongomodels import CodeEntityState, CodeGroupState, Commit, FileAction


def createModifiedSources():
    # connect to database
    dbConnect()
    
    for project in projects.keys():
        path = Path(ENV['PROJECTDIR']) / project / 'modified_classes'
        if not path.is_dir():
            path.mkdir()
        with open(Path(ENV['PROJECTDIR']) / project / 'bugs.csv') as f:
            modified = {}
            # calculate number of bugs for this project
            number_of_bugs = sum(1 for line in f)
            for i in range(1, number_of_bugs):
                bug = parseBug(project, str(i))
                modified[bug.id] = []
                # commit of the bugfix
                commit_fixed = Commit.objects().get(revision_hash=bug.rev_fixed)
                # get files modified in this commit
                for file_action in FileAction.objects(commit_id=commit_fixed.id).only('id', 'file_id'):
                    # get code entities corresponding to this commit and file with type 'class'
                    for code_entity in (CodeEntityState.objects(file_id=file_action.file_id, commit_id=commit_fixed.id)
                                                       .filter(ce_type = 'class')
                                                       .only('cg_ids', 'long_name')):
                        # make sure the code entity is not an inner class
                        for code_group_id in code_entity.cg_ids:
                            if (CodeGroupState.objects(id=code_group_id).filter(cg_type = 'package').count() > 0):
                                modified[bug.id].append(code_entity.long_name)
            # write modified classes
            for i in range(1, number_of_bugs):
                with open(path /  (str(i) + '.src'), 'w') as file:
                    file.write('\n'.join(modified[str(i)]))
