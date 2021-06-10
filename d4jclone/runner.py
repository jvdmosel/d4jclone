#!/usr/bin/python3

import argparse
import sys

import d4jclone.core.pids as pids
import d4jclone.core.bids as bids
import d4jclone.core.info as info
import d4jclone.core.checkout as checkout
import d4jclone.core.compile as compile
import d4jclone.core.test as test
import d4jclone.test as createTest

def fill(s):
    return s + '.' * (75-len(s)) + ' ' if len(s) < 75 else s

class D4jclone(object):
    
    def __init__(self):
        parser = argparse.ArgumentParser(description='d4jclone')
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()
        
    def info(self):
        parser = argparse.ArgumentParser(description='Info parser')
        parser.add_argument('-p', help='The id of the project for which the information shall be printed', required=True)
        parser.add_argument('-b', help='The id of the bug for which the information shall be printed', required=False)
        args = parser.parse_args(sys.argv[2:])
        info.info(args.p, args.b)
    
    def pids(self):
        pids.pids()
    
    def bids(self):
        parser = argparse.ArgumentParser(description='Bug ID parser')
        parser.add_argument('-p', help='The ID of the project for which the list of bug IDs is requested', required=True)
        args = parser.parse_args(sys.argv[2:])
        bids.bids(args.p)
    
    def checkout(self):
        parser = argparse.ArgumentParser(description='Checkout parser')
        parser.add_argument('-p', help='The id of the project for which a particular version shall be checked out', required=True)
        parser.add_argument('-v', help='The version id that shall be checked out', required=True)
        parser.add_argument('-w', help='The working directory to which the buggy or fixed project version shall be checked out', required=True)
        args = parser.parse_args(sys.argv[2:])
        checkout.checkout(args.p, int(args.v[:1]), args.v[1:], args.w)
        
    def compile(self):
        compile.compile()
        
    def test(self):
        parser = argparse.ArgumentParser(description='Test parser')
        parser.add_argument('-w', help='The working directory of the checked-out project version. Default is the current directory.', required=False)
        parser.add_argument('-r', help='Only execute relevant developer-written tests. By default all developer-written tests of the checked-out project version are executed.', required=False)
        parser.add_argument('-t', help='Only run this single test method. By default all tests are executed. Format: <test_class>::<test_method>.', required=False)
        parser.add_argument('-s', help='The archive file name of an external test suite. The default test suite is the developer-written test suite of the checked-out project version', required=False)
        args = parser.parse_args(sys.argv[2:])
        test.test(args.w, args.r, args.t, args.s)

def main():
    D4jclone()
    #metadata is specific to system, cannot upload as that, generate path on the fly (do not save)?
    
if __name__ == '__main__':
    main()
