from diagrams import Cluster, Diagram, Node, Edge
from diagrams.aws.engagement import Connect
from diagrams.aws.general import User
from diagrams.generic.device import Mobile
from diagrams.programming.language import Python


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
  # Global nodes
  script = Python("start_outbound.py")
  mobile = Mobile("External Call")
  start_outbound = Connect("Start Outbound\nVoice Contact")
  callback_queue = Connect("CallbackQueue")

  # Inbound flow
  with Cluster("CallbackInbound\nContact Flow"):
    transfer_to_unserviced_queue = Connect("Transfer to\nUnserviced\nQueue")
    end_current_call_inbound = Connect("End\nCurrent\nCall")

  # Outbound flow
  with Cluster("CallbackOutbound\nContact Flow"):
    set_outbound_number = Connect("Set\nOutbound\nNumber")
    set_agent_whisper = Connect("Set\nAgent\nWhisper")
    transfer_to_callback_queue = Connect("Transfer to\nCallback\nQueue")
    end_current_call_outbound = Connect("End\nCurrent\nCall")

    (
      set_outbound_number
      >> set_agent_whisper
      >> transfer_to_callback_queue
      >> end_current_call_outbound
    )
    transfer_to_callback_queue >> callback_queue

  end_current_call_outbound >> Edge(label="Terminates") >> end_current_call_inbound

  # Agent whisper
  with Cluster("CallbackAgentWhisper\nContact Flow"):
    agent = User("Agent")
    agent_prompt = Connect("Play\nPrompt")

    agent >> agent_prompt

  callback_queue >> Edge(label="Dequeue", style="dashed") >> agent

  # Outbound whisper
  with Cluster("CallbackOutboundWhisper\nContact Flow"):
    set_caller_id = Connect("Set\nCallerId")
    customer = User("Customer")
    two_way = Connect("Two-Way\nCall")

    set_caller_id >> Edge(label="Dial") >> customer >> Edge(label="Answer") >> two_way

  # Global edges
  agent_prompt >> set_caller_id

  script >> Edge(label="Call with\nattributes") >> start_outbound
  start_outbound >> Edge(label="Destination\nNumber") >> mobile
  start_outbound >> Edge(label=" Outbound\nFlow") >> set_outbound_number
  mobile >> Edge(label="Incoming\nCall") >> transfer_to_unserviced_queue

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
