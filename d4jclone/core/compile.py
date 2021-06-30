from pathlib import Path
from subprocess import PIPE, run

from d4jclone.parser.checkoutParser import parseCheckout
from d4jclone.util.formatting import fill

def compile(workdir = None, task = 'compile', arg = 'compile'):
    workdir = Path(workdir) if workdir != None else Path.cwd
    checkout = parseCheckout(workdir)
    print(fill('Running ant (' + task + ')'), end ='')
    args = ['ant', '-Dbasedir=' + str(workdir), '-Dprojectdir=' + str(checkout.project_dir), '-buildfile', checkout.project.build_file, arg]
    result = run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if 'BUILD SUCCESSFUL' in result.stdout:
        print('OK')
    else:
        print(checkout.rev)
        print(result.stdout, result.stderr)