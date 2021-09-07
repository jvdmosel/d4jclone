from d4jclone.util.projects import projects

def pids():
    """Prints all project ids.
    """
    
    for pid in projects.keys():
        print(pid)