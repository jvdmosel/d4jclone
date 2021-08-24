from d4jclone.config import ENV
from pathlib import Path
from subprocess import PIPE, run

from d4jclone.parser.checkoutParser import parseCheckout
from d4jclone.util.formatting import fill

def compile(workdir = None, task = 'compile', arg = 'compile', testdir = None):
    workdir = Path(workdir) if workdir != None else Path.cwd()
    checkout = parseCheckout(workdir)
    print(fill('Running ant (' + task + ')', '.', 75), end ='', flush=True)
    base_args = ['ant', '-Dbasedir=' + str(workdir), '-Dprojectdir=' + str(checkout.project_dir), '-Dlibdir=' + ENV['LIBDIR']]
    args = base_args + ['-buildfile', checkout.project.build_file, 'clean']
    run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if testdir != None:
        args = base_args + ['-Dtest.dir=' + str(testdir), '-buildfile', checkout.project.build_file, arg]
    else:
        args = base_args + ['-buildfile', checkout.project.build_file, arg]
    result = run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if 'BUILD SUCCESSFUL' in result.stdout:
        print('OK')
    else:
        print('FAILED')
        print(result.stdout, result.stderr)