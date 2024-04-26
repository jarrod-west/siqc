from diagrams import Cluster, Diagram, Node, Edge
from diagrams.aws.integration import SQS
from diagrams.aws.compute import Lambda
from diagrams.aws.engagement import Connect
from diagrams.aws.general import User
from diagrams.generic.device import Mobile


class StartNode(Node):
  def __init__(self, label: str) -> None:
    super().__init__(
      label,
      labelloc="c",
      style="filled",
      fillcolor="black",
      fontcolor="white",
      shape="circle",
    )


class FlowNode(Node):
  def __init__(self, label: str) -> None:
    super().__init__(
      label,
      labelloc="c",
      style="filled,rounded",
      fillcolor="#1c6beb",
      fontcolor="white",
    )


with Diagram(
  "\nScheduled In-Queue Callbacks",
  filename="./docs/siqc",
  show=False,
  graph_attr={"splines": "polyline", "fontsize": "24"},
):
  start = StartNode("Start")
  lambda_node = Lambda("Callback Lambda")
  sqs = SQS("Callback Queue")
  mobile = Mobile("External Call")
  end = StartNode("End")

  start_outbound = Connect("Start Outbound\nVoice Contact")

  with Cluster("CallbackInbound\nContact Flow"):
    retrieve = Connect("Retrieve\nCallback\nDetails")
    set_outbound_number = Connect("Set\nOutbound\nNumber")
    callback_queue = Connect("Transfer to\nCallback\nQueue")
    end_current_call_inbound = Connect("End\nCurrent\nCall")

    retrieve >> set_outbound_number >> callback_queue >> end_current_call_inbound
    end_current_call_inbound >> end

  with Cluster("CallbackOutbound\nContact Flow"):
    transfer_to_queue = Connect("Transfer to\nUnserviced\nQueue")
    end_current_call_outbound = Connect("End\nCurrent\nCall")

    transfer_to_queue >> Edge(label="Wait", style="dashed") >> end_current_call_outbound
    end_current_call_inbound >> end_current_call_outbound
    end_current_call_outbound >> end

  start >> Edge(label=" Start Outbound\nVoice Contact") >> start_outbound
  start_outbound >> Edge(label="Destination\nNumber") >> mobile
  start_outbound >> Edge(label=" Outbound\nFlow") >> transfer_to_queue
  mobile >> Edge(label="Incoming\nCall") >> retrieve

  start >> Edge(label="Set\nCallback\nNumber") >> lambda_node
  retrieve >> Edge(label="Retrieve \nCallback \nDetails", reverse=True) >> lambda_node
  lambda_node >> Edge(label=" push/pop\ncallback", reverse=True) >> sqs

with Diagram(
  "\nIn-Queue Callbacks",
  filename="./docs/iqc",
  show=False,
  graph_attr={"fontsize": "24"},
):
  start = StartNode("Start")

  connect_inbound = Connect("Connect\nPhone Number")
  connect_callback = Connect("Callback Queue")

  with Cluster("Inbound Contact Flow"):
    set_outbound_number = Connect("Set\nOutbound\nNumber")
    callback_queue = Connect("Transfer to\nCallback\nQueue")
    end_current_call = Connect("End\nCurrent\nCall")

    set_outbound_number >> callback_queue >> end_current_call

  with Cluster("Callback"):
    agent = User("Agent")
    callback = Connect("Callback")
    customer = User("Customer")
    two_way = Connect("Two-Way\nCall")

    (
      agent
      >> Edge(label="Accept")
      >> callback
      >> Edge(label="Dial")
      >> customer
      >> Edge(label="Accept")
      >> two_way
    )

  callback_queue >> Edge(label="Transfer") >> connect_callback
  connect_callback >> Edge(label="Dequeue", style="dashed") >> agent

  connect_inbound >> set_outbound_number
  start >> Edge(label="Call") >> connect_inbound

with Diagram(
  "\nStart Outbound Voice Contact",
  filename="./docs/sovc",
  show=False,
  graph_attr={"fontsize": "24"},
):
  start = StartNode("Start")
  outbound = Connect("Start Outbound\nVoice Contact")

  with Cluster("Outbound Call"):
    customer = User("Customer")
    connect_call = Connect("Outbound Queue")
    agent = User("Agent")
    two_way = Connect("Two-Way\nCall")

    (
      customer
      >> Edge(label="Answer")
      >> connect_call
      >> Edge(label="Dequeue")
      >> agent
      >> Edge(label="Accept")
      >> two_way
    )

  start >> outbound >> Edge(label="Dial") >> customer
