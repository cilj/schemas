#!/usr/bin/env python

import glob, subprocess

def lock(file_path):
  args = ["git", "lfs", "lock", file_path]
  subprocess.call(args)

filter = '**/*.schema.json'

for file_path in glob.glob(filter, recursive = True):
  lock(file_path)

