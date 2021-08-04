
def fill(s, total_length, postfix = ' '):
    return s + '.' * (total_length-len(s)) + postfix if len(s) < total_length else s