
def fill(s):
    return s + '.' * (75-len(s)) + ' ' if len(s) < 75 else s