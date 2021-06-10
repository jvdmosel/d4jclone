from d4jclone.util.projects import projects

def pids():
    for pid in projects.keys():
        print(pid)