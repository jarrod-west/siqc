import json
from pathlib import Path

CLOUDFORMATION_TEMPLATE = "cloudformation.yaml.j2"

FLOW_NAMES = [
  "Callback_Inbound"
]

FLOW_DEPLOY_DIR = Path().joinpath("deploy", "flows")
FLOW_DEPLOY_CONTENT_DIR = FLOW_DEPLOY_DIR.joinpath("content")

FLOW_EXPORT_DIR = Path().joinpath("export", "flows")
FLOW_EXPORT_CONTENT_DIR = FLOW_EXPORT_DIR.joinpath("content")


def untemplate_filename(template_name):
  return ".".join(template_name.split(".")[:-1])

def file_path(directory, name):
  return directory.joinpath(name + ".json")

def write_file(directory, name, content):
  with open(file_path(directory, name), "w") as outfile:
    json.dump(content, outfile, indent=2)

def read_file(directory, name):
  with open(file_path(directory, name)) as infile:
    return json.load(infile)

def logical_id(name):
  # Create a valid cloudformation logical ID by removing "word-delims" and forcing upper camel case
  delims = " -_"

  tokens = [name]

  for delim in delims:
    start = len(tokens)

    for i in range(0, start):
      tokens += tokens[i].split(delim)

    tokens = tokens[start:]

  return "".join([token[0].upper() + token[1:].lower() for token in tokens])