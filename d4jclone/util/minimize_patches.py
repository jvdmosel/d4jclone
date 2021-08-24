from collections import Counter
from pathlib import Path

from d4jclone.config import ENV
from d4jclone.parser.bugParser import parseBug
from d4jclone.parser.projectParser import parseProject
from d4jclone.util.db import dbConnect
from pycoshark.mongomodels import Commit, FileAction, Hunk


def getVerifiedBugfix(bug):
    verified = []
    # connect to database
    dbConnect()
    # commit of the bugfix
    commit_fixed = Commit.objects().get(revision_hash=bug.rev_fixed)
    # get files modified in this commit
    for file_action in FileAction.objects(commit_id=commit_fixed.id).only('id', 'file_id'):
        for hunk in (Hunk.objects(file_action_id=file_action.id)
                     .filter(lines_verified__bugfix__ne = None)
                     .only('content', 'lines_verified')):
            lines = hunk.content.splitlines()
            verified_lines = []
            for i in hunk.lines_verified['bugfix']:
                verified_lines.append(lines[i])
            verified.extend(verified_lines)
    return verified

def minimizePatch(bug):
    # get verified bugfix from database
    # however we require the fixed to buggy version direction
    bugfix = getVerifiedBugfix(bug)
    # helper dict to swap - to + and vice versa
    swap = {'-': '+', '+': '-'}
    # helper function to reverse changes
    reverse = lambda x : swap[x[0]] + x[1:]
    # get the lines with reversed changes, order is different from a normal git patch
    reverse_bugfix = [reverse(x) for x in bugfix]
    # since order is more or less random and lines do not have to be unique
    # we need some way to check whether a line from the reversed bugfix is already part of the patch
    # count the number of times each line appears in the bugfix
    reverse_bugfix = Counter(reverse_bugfix)
    patch_path = Path(ENV['PROJECTDIR']) / bug.project / 'patches' / (bug.id + '.src.patch')
    if not patch_path.is_file():
        return
    # read in the unminimized patch, this requires the create_patches script to be run first
    patch = []
    with open(patch_path, 'r') as p:
        patch = p.readlines()
    minimized = []
    for line in patch:
        # check if the line is a change
        if (line[0] == '+' or line[0] == '-') and not (line[:3] == '+++' or line[:3] == '---'):
            # patch lines contain newlines -> strip
            # check if line is in the bugfix
            if line.strip() not in reverse_bugfix.keys():
                # no -> remove line from patch
                continue
            elif reverse_bugfix[line.strip()] == 0:
                # counter is already zero -> remove line from patch
                continue
            else:
                # line is part of the bugfix -> keep
                reverse_bugfix[line.strip()] -= 1
        minimized.append(line)
    # write patch
    with open(patch_path, 'w') as p:
        for line in minimized:
            p.write(line)
        
    
def minimizePatches(pid):
    project = parseProject(pid)
    for i in range(1, project.number_of_bugs):
        bug = parseBug(project.id, str(i))
        minimizePatch(bug)
