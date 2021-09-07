from d4jclone.config import ENV
from pathlib import Path
from subprocess import PIPE, run

from d4jclone.parser.checkoutParser import parseCheckout
from d4jclone.util.formatting import fill

def compile(workdir = None, task = 'compile', arg = 'compile', testdir = None):
    """ Compile a checked-out project version.

    Args:
        workdir (str, optional): The working directory of the checked-out project version. Defaults to the current working directory.
        task (str, optional): The compile task that should be printed, viable tasks are 'compile', 'compile.tests', 'compile.gen.tests'. Defaults to 'compile'.
        arg (str, optional): The compile argument (ant target), viable targets are 'compile', 'compile-tests', 'compile-gen-tests'. Defaults to 'compile'.
        testdir (str, optional): The test directory, required for 'compile-gen-tests'. Defaults to None.
    """
    
    # TODO: Refactor task and arg to single variable target, since only '.' and '-' are different.
    workdir = Path(workdir) if workdir != None else Path.cwd()
    checkout = parseCheckout(workdir)
    print(fill('Running ant (' + task + ')', '.', 75), end ='', flush=True)
    # default arguments common for all tasks
    base_args = ['ant', '-Dbasedir=' + str(workdir), '-Dprojectdir=' + str(checkout.project_dir), '-Dlibdir=' + ENV['LIBDIR']]
    # clean before compile
    # optional?
    args = base_args + ['-buildfile', checkout.project.build_file, 'clean']
    run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    # check if testdir is provided -> compile-gen-tests
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