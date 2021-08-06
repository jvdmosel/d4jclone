#!/usr/bin/python3

import argparse
from d4jclone.core.export import export
import sys

import d4jclone.core.pids as pids
import d4jclone.core.bids as bids
import d4jclone.core.info as info
import d4jclone.core.checkout as checkout
import d4jclone.core.compile as compile
import d4jclone.core.test as test
import d4jclone.core.env as env
import d4jclone.core as core
import d4jclone.test as createTest
import d4jclone.util.create_patches as patches
import d4jclone.util.create_triggering_tests as triggeringTests
import d4jclone.util.create_relevant_tests as relevantTests
import d4jclone.util.verified_lines as verified_lines
from d4jclone.util.create_layout import createLayout

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
        checkout.checkout(args.p, int(args.v[:len(args.v)-1]), args.v[len(args.v)-1:], args.w)
        
    def compile(self):
        parser = argparse.ArgumentParser(description='Compile parser')
        parser.add_argument('-w', help='The working directory of the checked-out project version. Default is the current directory.', required=False)
        args = parser.parse_args(sys.argv[2:])
        compile.compile(args.w)
        
    def test(self):
        parser = argparse.ArgumentParser(description='Test parser')
        parser.add_argument('-w', help='The working directory of the checked-out project version. Default is the current directory.', required=False)
        parser.add_argument('-r', help='Only execute relevant developer-written tests. By default all developer-written tests of the checked-out project version are executed.', required=False)
        parser.add_argument('-t', help='Only run this single test method. By default all tests are executed. Format: <test_class>::<test_method>.', required=False)
        parser.add_argument('-s', help='The archive file name of an external test suite. The default test suite is the developer-written test suite of the checked-out project version', required=False)
        args = parser.parse_args(sys.argv[2:])
        test.test(args.w, args.t, args.r, args.s)
    
    def env(self):
        env.env()
        
    def export(self):
        parser = argparse.ArgumentParser(description='Export parser')
        parser.add_argument('-p', help='Export the value(s) of this property.', required=True)
        parser.add_argument('-o', help='Write output to this file (optional). By default the script prints the value(s) of the property to stdout. Note that all diagnostic messages are sent to stderr.', required=False)
        parser.add_argument('-w', help='The working directory of the checked-out project version (optional). Default is the current directory.', required=False)
        args = parser.parse_args(sys.argv[2:])
        export.export(args.p, args.o, args.w)
        

def main():
    D4jclone()
    
    
if __name__ == '__main__':
    main()
