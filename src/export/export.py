import json

from shared.clients.connect_client import ConnectClient
from shared.logger import logger
from shared.utils import FLOW_EXPORT_DIRECTORY, FLOW_NAMES, read_parameters


def export_flow(connect_client: ConnectClient, flow_name: str, flow_arn: str) -> None:
  """Exports a flow's content to a file.

  Args:
      connect_client (ConnectClient): The connect client
      flow_name (str): The name of the flow to export
      flow_arn (str): The ARN of the flow to export
  """
  logger.info(f"Exporting flow {flow_name}...")

  # Retrieve the flow
  flow = connect_client.get_contact_flow(flow_arn)

  # Separate out the content and save it to a file
  content = flow.pop("Content")

  outpath = FLOW_EXPORT_DIRECTORY.joinpath(f"{flow_name}.json")
  with open(outpath, "w") as outfile:
    # Loading and dumping allows us to format the file for better readability
    json.dump(json.loads(content), outfile, indent=2)

  logger.info("Flow export complete")


def export() -> None:
  """Retrieve contact flow details and export all of them to files."""
  parameters = read_parameters()

  # Create the target directories
  FLOW_EXPORT_DIRECTORY.mkdir(exist_ok=True, parents=True)

  connect_client = ConnectClient(parameters["InstanceAlias"])

  # Map the ids
  flow_summary_list = connect_client.get_flow_summaries(list(FLOW_NAMES.values()))
  flow_arns: dict[str, str] = {}
  for flow_summary in flow_summary_list:
    flow_arns[flow_summary["Name"]] = flow_summary["Arn"]

  # Export each flow
  for flow_name in FLOW_NAMES.values():
    export_flow(connect_client, flow_name, flow_arns[flow_name])

  logger.info("Export completed successfully")


if __name__ == "__main__":
  export()
