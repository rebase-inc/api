#!/usr/bin/env python

from argparse import ArgumentParser, Namespace
from importlib import import_module
from pathlib import Path

parser = ArgumentParser(description='Manage Rebase\'s Backend')
subparsers = parser.add_subparsers()


for entry in Path('parsers').glob('*.py'):
    if entry.is_file() and not entry.name.startswith('__'):
        module = import_module('parsers.'+entry.stem)
        module.add_parser(subparsers)

if __name__ == "__main__":
    args = parser.parse_args()
    if args ==  Namespace():
        args = parser.parse_args(['--help'])
    args.func(args)
