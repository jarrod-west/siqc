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
  graph_attr={"fontsize": "24"},
):
  start = StartNode("Start")
  lambda_node = Lambda("Callback Lambda")
  sqs = SQS("Callback Queue")
  mobile = Mobile("External Call")
  end = StartNode("End")

  with Cluster("Connect"):
    connect = Connect("Connect Instance")

    with Cluster("CallbackInbound Contact Flow"):
      start_inbound = FlowNode("Start")
      retrieve = FlowNode("Retrieve\nCallback\nDetails")
      set_outbound_number = FlowNode("Set\nOutbound\nNumber")
      callback_queue = FlowNode("Transfer to\nCallback\nQueue")

      start_inbound >> retrieve >> set_outbound_number >> callback_queue >> end

    with Cluster("CallbackOutbound Contact Flow"):
      start_outbound = FlowNode("Start")
      transfer_to_queue = FlowNode("Transfer\nto\nUnserviced\nQueue")

      start_outbound >> transfer_to_queue >> end

  start >> Edge(label=" Start Outbound\nVoice Contact") >> connect
  connect >> Edge(label="Destination\nNumber") >> mobile
  connect >> Edge(label=" Outbound\nFlow") >> start_outbound
  mobile >> Edge(label="Incoming\nCall") >> start_inbound

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

  connect_inbound = Connect("Connect Phone Number")
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
