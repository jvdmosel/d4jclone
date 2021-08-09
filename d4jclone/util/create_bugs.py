import csv
import subprocess
import sys
from datetime import timedelta, timezone
from pathlib import Path

import yaml
from d4jclone.util.projects import projects
from mongoengine import connect
from pycoshark.mongomodels import Commit, FileAction, Hunk, Issue, Project, VCSSystem
from d4jclone.util.db import dbConnect


# visualization, source: https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration       - Required  : current iteration (Int)
        total           - Required  : total iterations (Int)
        prefix          - Optional  : prefix string (Str)
        suffix          - Optional  : suffix string (Str)
        decimals        - Optional  : positive number of decimals in percent complete (Int)
        bar_length      - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def to_ISO_8601(dt, utc_offset):
    # add utc offset to datetime and convert to YYYY:MM:DD HH:MM:SS ZZZZ format
    iso = str(dt.replace(tzinfo=timezone(timedelta(minutes=utc_offset))))
    return iso[:-6] + ' ' + iso[-6:-3] + iso[-2:]

def createBugs():
    # clean projects dir
    path = Path.cwd() / 'd4jclone/projects'
    if not path.is_dir():
        path.mkdir()
    
    dbConnect()
    
    # csv headers
    headers = ['bug.id', 'revision.id.buggy', 'revision.id.fixed', 
               'revision.date.buggy', 'revision.date.fixed', 
               'report.id', 'report.url']
    
    for project_id, project in projects.items():
        bugs = []
        
        # fetch validated bugfix commits fixing exactly one issue, ordered by committer_date
        internal_id = Project.objects(name=project).only('id').get().id
        vcssystem_id = VCSSystem.objects(project_id=internal_id).only('id').get().id
        commits = (Commit.objects(vcs_system_id=vcssystem_id)
                         .filter(labels__validated_bugfix = True, fixed_issue_ids__1__exists = False)
                         .only('id', 'revision_hash', 'parents', 'committer_date', 
                               'committer_date_offset', 'fixed_issue_ids'))
        for i, commit in enumerate(commits):
            # fetch fixed issues for this commit
            print_progress(i, len(commits), suffix=project_id, bar_length=20)
            for issue_id in commit.fixed_issue_ids:
                # check whether the issue was fixed in one commit and has only one parent
                fixed_in_one_commit = (commits.filter(fixed_issue_ids__contains=issue_id).count() == 1)
                if fixed_in_one_commit and len(commit.parents) == 1:
                    issue = Issue.objects(id=issue_id).only('external_id', 'issue_type_verified').get()
                    # verify that the issue is indeed a bug
                    if issue.issue_type_verified == 'bug':
                        # external id and url in the issue tracking system
                        ext = issue.external_id
                        url = 'https://issues.apache.org/jira/browse/' + ext
                        
                        # revision hashes of buggy and fixed version
                        rid_fixed = commit.revision_hash
                        rid_buggy = commit.parents[0]
                        
                        commit_buggy = Commit.objects(revision_hash=rid_buggy).only('committer_date', 'committer_date_offset').get()
                        
                        # revision datetime with offset
                        rdate_buggy = to_ISO_8601(commit_buggy.committer_date, commit_buggy.committer_date_offset)
                        rdate_fixed = to_ISO_8601(commit.committer_date, commit.committer_date_offset)
                        
                        # make sure verified lines exist for this bugfix
                        commit_fixed = Commit.objects().get(revision_hash=rid_fixed)
                        hunks = 0
                        for file_action in FileAction.objects(commit_id=commit_fixed.id).only('id', 'file_id'):
                            hunks = hunks + Hunk.objects(file_action_id=file_action.id).filter(lines_verified__bugfix__ne = None).count()
                        if hunks >= 1:
                            bugs.append({'revision_id_buggy': rid_buggy, 'revision_id_fixed': rid_fixed,
                                         'revision_date_buggy': rdate_buggy, 'revision_date_fixed': rdate_fixed, 
                                         'external_id': ext, 'report_url': url})
            print_progress(i, len(commits), suffix=project_id, bar_length=20)
        # check whether validated bugs exist for this project
        if len(bugs) > 0:
            # create project dir
            project_path = path / project_id
            if not project_path.is_dir():
                project_path.mkdir()
            
            # write csv
            with open(project_path / 'bugs.csv', 'w', newline='') as bugs_csv:
                # write headers
                csv_writer = csv.writer(bugs_csv)
                csv_writer.writerow(headers)
            
                # sort bugs chronological, determined by external id
                bugs = sorted(bugs, key=lambda k: int(k['external_id'].rsplit('-', 1)[1]))
                # write bugs to csv
                for _id, bug in enumerate(bugs, 1):
                    (csv_writer.writerow([_id, bug['revision_id_buggy'], bug['revision_id_fixed'],
                                          bug['revision_date_buggy'], bug['revision_date_fixed'], 
                                          bug['external_id'], bug['report_url']]))
        print_progress(len(commits), len(commits), suffix=project_id, bar_length=20)
