import jinja2
from pathlib import Path

from src.shared import FLOW_DEPLOY_DIR, FLOW_DEPLOY_CONTENT_DIR, FLOW_EXPORT_CONTENT_DIR, FLOW_EXPORT_DIR, FLOW_NAMES, logical_id, read_file, write_file
from src.logger import logger


CLOUDFORMATION_TEMPLATE = "cloudformation.yaml.j2"


def build_arn_map(node, arn_map):
  # Recursively walk the contact flow to find the ARNs
  if isinstance(node, list):
    for child in node:
      build_arn_map(child, arn_map)
  elif isinstance(node, dict):
    if "id" in node and "text" in node:
      arn_map[node["id"]] = node["text"]
    else:
      for _, child in node.items():
        build_arn_map(child, arn_map)


def replace_arns(node, arn_map):
  # Recursively walk the contact flow to find the ARNs
  if isinstance(node, list):
    for child in node:
      replace_arns(child, arn_map)
  elif isinstance(node, dict):
    for key, child in node.items():
      if isinstance(child, str) and child in arn_map:
        resource_type = child.split("/")[-2]
        node[key] = "{{" + f"resources['{resource_type}']['{arn_map[child]}']" + "}}"
      else:
        replace_arns(child, arn_map)


def templatise_flow(flow_name):
  logger.info(f"Templatising flow {flow_name}")

  flow = read_file(FLOW_EXPORT_DIR, flow_name)
  content = read_file(FLOW_EXPORT_CONTENT_DIR, flow_name)

  arn_map = {}
  build_arn_map(content, arn_map)
  replace_arns(content, arn_map)

  # TODO: Write the content file
  write_file(FLOW_DEPLOY_CONTENT_DIR, flow_name, content)

  id = logical_id(flow_name)

  logger.info(f"Flow templatise complete")

  return id, flow


def templatise():
  flows = {}

  # Templatise each flow
  for flow_name in FLOW_NAMES:
    logical_id, flow = templatise_flow(flow_name)
    flows[logical_id] = flow

  # Create the templatised cloudformation
  env = jinja2.Environment(loader=jinja2.FileSystemLoader(Path(__file__).parent))
  template = env.get_template(CLOUDFORMATION_TEMPLATE)
  flow_file = template.render(flows=flows)

  with open(FLOW_DEPLOY_DIR.joinpath(CLOUDFORMATION_TEMPLATE), "w") as outfile:
    outfile.write(flow_file)

  logger.info(f"Templatise completed successfully")

if __name__ == '__main__':
  templatise()
