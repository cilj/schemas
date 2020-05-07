#!/usr/bin/env python

import glob, json, subprocess

def unlock(entry):
    lock_id = entry.get('id')
    args = ['git', 'lfs', 'unlock', '--id=' + lock_id]
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(p.stdout.decode().strip() + " File " + entry.get('path'))
    if p.stderr:
      print(p.stderr.decode().strip())

filter = "**/*.schema.json"

args = ['git', 'lfs', 'locks', '--json']
p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
entries = json.loads(p.stdout)

if len(entries) == 0:
  print("No locked schemas found")
  exit(1)

for entry in entries:
  unlock(entry)
