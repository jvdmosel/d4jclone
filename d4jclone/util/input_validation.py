from d4jclone.parser.projectParser import parseProject
from d4jclone.util.projects import projects

def is_valid_pid(pid):
    return pid in projects.keys()
    
def is_valid_bid(pid, bid):
    project = parseProject(pid)
    return 0 < int(bid) <= project.number_of_bugs+1
    
def is_valid_vid(pid, vid):
    return is_valid_bid(pid, vid[:-1]) and (vid[-1] == 'b' or vid[-1] == 'f')