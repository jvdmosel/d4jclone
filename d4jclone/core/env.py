import os
import re
from subprocess import PIPE, run

from d4jclone.config import ENV
from d4jclone.util.formatting import fill


def env():
    env = os.environ
    sep = '-' * 80
    header = 'D4JCLONE Execution Enviroment'
    print(sep)
    print((' ' * int((80 - len(header)) / 2))
          + 'D4JCLONE Execution Enviroment' 
          + (' ' * int((80 - len(header)) / 2)))
    print(sep)
    # General enviroment
    print(fill('PWD', 30, '') + env['PWD'])
    print(fill('SHELL', 30, '') + env['SHELL'])
    print(fill('TZ', 30, '') + ENV['TZ'])
    # Java enviroment
    print(fill('JAVA_HOME', 30, '') + run_cmd('echo $JAVA_HOME'))
    print(fill('Java Exec', 30, '') + run_cmd('which java'))
    print(fill('Java Exec Resolved', 30, '') + run_cmd('realpath $(which java)'))
    print('Java Version:' + run_multiline_cmd('java -version 2>&1'))
    # VCS enviroment
    print(fill('Git version', 30, '') + run_cmd('git --version'))
    print(fill('SVN version', 30, '') + run_cmd('svn --version --quiet'))
    print(fill('Perl version', 30, '') + str(re.search(r'v\d+\.\d+\.\d+', run_cmd('perl -v')).group()))
    print(sep)

def run_multiline_cmd(args):
    result = run(args, shell=True, stdout=PIPE, stderr=PIPE)
    out = result.stdout.decode('ascii').split('\n')[:-1]
    if len(out) == 0:
        return '(none)'
    else:
        s = ''
        for line in out:
            s += '\n\t' + line
        return s

def run_cmd(args):
    result = run(args, shell=True, stdout=PIPE, stderr=PIPE)
    out = result.stdout.strip()
    return '(none)' if len(out) == 0 else out.decode('ascii')
