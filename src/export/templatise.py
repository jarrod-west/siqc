import json
from typing import Any, Callable

from shared.logger import logger
from shared.utils import (
  FLOW_CONTENT_DIRECTORY,
  FLOW_NAMES,
  FLOW_EXPORT_DIRECTORY,
  create_logical_id,
)


# Recursive walker
def walk_content(
  parent: Any,
  node: Any,
  arn_map: dict[str, str],
  operation: Callable[[Any, Any, dict[str, str]], bool],
) -> None:
  # Recursively walk the contact flow
  if isinstance(node, list):
    # List: call on each child
    if operation(parent, node, arn_map):
      for child in node:
        walk_content(node, child, arn_map, operation)
  elif isinstance(node, dict):
    if operation(parent, node, arn_map):
      for child in node.values():
        walk_content(node, child, arn_map, operation)
  else:
    operation(parent, node, arn_map)


# Recursive walk operations
def update_arn_map(_: Any, node: Any, arn_map: dict[str, str]) -> bool:
  # Relevant ARNs are in a node with "id" and "text" parameters
  if isinstance(node, dict) and "id" in node and "text" in node:
    arn_map[node["id"]] = node["text"]
    return False

  return True


def replace_arns_with_templates(
  parent: Any, node: Any, arn_map: dict[str, str]
) -> bool:
  if isinstance(node, str) and node in arn_map:
    # Find the current node's key
    key = list(parent.keys())[list(parent.values()).index(node)]

    # Update the value
    parent[key] = "{{" + f"resources['{create_logical_id(arn_map[node])}']" + "}}"
    return False

  return True


def templatise_flow(flow_name: str) -> None:
  logger.info(f"Templatising flow {flow_name}...")

  # Load the exported file
  inpath = FLOW_EXPORT_DIRECTORY.joinpath(f"{flow_name}.json")
  with open(inpath) as infile:
    content = json.load(infile)

  # Replace the ARNs with the jinja2 templated values
  arn_map: dict[str, str] = {}
  walk_content(None, content, arn_map, update_arn_map)
  walk_content(None, content, arn_map, replace_arns_with_templates)

  # Write the templated file
  outpath = FLOW_CONTENT_DIRECTORY.joinpath(f"{flow_name}.json")
  with open(outpath, "w") as outfile:
    json.dump(content, outfile, indent=2)

  logger.info("Flow templatise complete")


def templatise() -> None:
  # Templatise each flow
  for flow_name in FLOW_NAMES.values():
    templatise_flow(flow_name)

  logger.info("Templatise completed successfully")


if __name__ == "__main__":
  templatise()
