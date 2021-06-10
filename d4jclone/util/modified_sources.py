import json
from pathlib import Path

from d4jclone.util.db import dbConnect
from d4jclone.parser.bugParser import parseBug
from d4jclone.util.projects import projects
from pycoshark.mongomodels import CodeEntityState, CodeGroupState, Commit, FileAction


def createModifiedSources():
    # connect to database
    dbConnect()
    
    for project in projects.keys():
        path = Path.cwd() / 'd4jclone/projects' / project
        with open(path / 'bugs.csv') as f:
            modified = {}
            # calculate number of bugs for this project
            number_of_bugs = sum(1 for line in f)
            for i in range(1, number_of_bugs):
                bug = parseBug(project, str(i))
                modified[bug.external_id] = []
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
                                modified[bug.external_id].append(code_entity.long_name)
            # write modified sources to json file
            with open(path /  'modified_sources.json', 'w') as json_file:
                json.dump(modified, json_file, indent=4)
