
def fill(seq, char, total_length, postfix = ' '):
    if len(seq) < total_length:
        return seq + char * (total_length-len(seq)) + postfix
    else:
        return seq