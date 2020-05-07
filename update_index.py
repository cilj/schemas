#!/usr/bin/env python

import os
import json
import yaml  # pip install pyyaml
from typing import Callable
from typing import IO
from jsonschema import validate  # pip install jsonschema
import requests # pip install requests
from urllib.parse import urljoin

def read_yaml(file: str):
    with open(file) as reader:
        value = yaml.safe_load(reader)
        return value


def read_json(file: str):
    with open(file) as reader:
        value = json.load(reader)
        return value

def read_url(url: str):
    with requests.get(url) as r:
        return r.json()


def write_to(file: str, src: Callable[[IO], None]):
    with open(file, mode="w") as writer:
        src(writer)


config = read_yaml("./_config.yml")
base_path = os.path.join(config["url"], config["baseurl"])
base_folder = config['baseurl']
base_uri = urljoin(config["url"], config["baseurl"])
families_yaml = open("./_data/schema_families.yaml")
listing = yaml.safe_load(families_yaml)
families_yaml.close()
families = list(listing["families"])

for f in families:
    if not os.path.exists(f["folder"]):
        families.remove(f)
        continue

    family_uri = os.path.join(base_uri, f["folder"])
    family_path = os.path.join(".", f["folder"])
    family_children = []
    f["uri"] = family_uri
    f["path"] = family_path.replace("./", "{s}/".format(s=base_folder))
    f["children"] = family_children
    f["noContent"] = True

    for child_dir in sorted(os.listdir(family_path)):
        child_uri = os.path.join(family_uri, child_dir)
        child_path = os.path.join(family_path, child_dir)

        if not os.path.isdir(child_path):
            continue

        child_versions = []
        child = {}
        family_children.append(child)
        child["uri"] = child_uri
        child["path"] = child_path.replace("./", "{s}/".format(s=base_folder))
        child["id"] = child_dir
        child["versions"] = child_versions

        for version_dir in sorted(os.listdir(child_path), reverse=True):
            version_uri = os.path.join(child_uri, version_dir)
            version_path = os.path.join(child_path, version_dir)
            version_schemas = []
            version_other_files = []
            version = {}
            child_versions.append(version)
            version["name"] = version_dir.replace("v", "").replace("_", ".")
            version["path"] = version_path.replace("./", "{s}/".format(s=base_folder))
            version["uri"] = version_uri
            version["schemas"] = version_schemas
            version["otherFiles"] = version_other_files

            version_files = os.listdir(version_path)
            schemas = [x for x in version_files if "schema.json" in x]
            other_files = [x for x in version_files if "schema.json" not in x]

            for s in schemas:
                schema_uri = os.path.join(version_uri, s)
                schema_path = os.path.join(version_path, s)
                schema = {}
                version_schemas.append(schema)
                schema["uri"] = schema_uri
                schema["path"] = schema_path.replace("./", "{s}/".format(s=base_folder))
                schema["fileName"] = s
                f.pop("noContent", None)
                schema_file = read_json(schema_path)
                schema_id = schema_file["$id"]
                if schema_id != schema_uri:
                    schema["error"] = "Schema uri does not match schema $id property!"
                root_schema = read_url(schema_file["$schema"])
                validate(instance=schema_file, schema=root_schema)

            for o in other_files:
                file_uri = os.path.join(version_uri, o)
                file_path = os.path.join(version_path, o)
                file = {}
                version_other_files.append(file)
                file["uri"] = file_uri
                file["path"] = file_path.replace("./", "{s}/".format(s=base_folder))
                file["fileName"] = o
                f.pop("noContent", None)
                other_file = read_json(file_path)
                validate(instance=other_file, schema=schema_file)

listing_json = json.dumps(listing, indent=2)

write_to("./_data/_schema_index.json", lambda w: w.write(listing_json))
write_to("./index.json", lambda w: w.write(listing_json))
