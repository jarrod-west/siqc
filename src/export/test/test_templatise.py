import json
from pytest_mock import MockerFixture

from export.templatise import (
  replace_arns_with_templates,
  templatise,
  templatise_flow,
  update_arn_map,
  walk_content,
)


def test_update_arn_map() -> None:
  arn_map: dict[str, str] = {}

  node = {"id": "mock id", "text": "mock text"}

  assert update_arn_map(None, node, arn_map) == False
  assert arn_map == {"mock id": "mock text"}

  arn_map = {}
  assert update_arn_map(None, {}, arn_map) == True
  assert update_arn_map(None, "foo", arn_map) == True
  assert update_arn_map(None, [], arn_map) == True


def test_replace_arns_with_templates() -> None:
  arn_map = {"mock id": "mock text"}

  nodes = {"foo": "mock id"}

  assert replace_arns_with_templates(nodes, "mock id", arn_map) == False
  assert nodes == {"foo": "{{resources['MockText']}}"}

  assert replace_arns_with_templates(nodes, "bar", arn_map) == True
  assert replace_arns_with_templates(nodes, {}, arn_map) == True
  assert replace_arns_with_templates(nodes, [], arn_map) == True


def test_walk_content() -> None:
  arn_map = {"mock id": "mock text"}

  nodes = [{"foo": "mock id"}, {"bar": "baz"}]

  walk_content(None, nodes, arn_map, replace_arns_with_templates)

  assert nodes == [{"foo": "{{resources['MockText']}}"}, {"bar": "baz"}]


def test_templatise_flow(mocker: MockerFixture) -> None:
  mock_content = {
    "content": {
      "meta": {"id": "mock id", "text": "mock text"},
      "foo": "mock id",
      "bar": "baz",
    }
  }

  mock_file = mocker.mock_open(read_data="open file")
  mocker.patch("builtins.open", mock_file)
  mock_load = mocker.patch.object(json, "load", return_value=mock_content)
  mock_dump = mocker.patch.object(json, "dump")

  templatise_flow("flow 1")

  assert mock_load.call_args == [(mock_file.return_value,), {}]
  assert mock_dump.call_args == [
    (
      {
        "content": {
          "meta": {"id": "{{resources['MockText']}}", "text": "mock text"},
          "foo": "{{resources['MockText']}}",
          "bar": "baz",
        }
      },
      mock_file.return_value,
    ),
    {"indent": 2},
  ]


def test_templatise(mocker: MockerFixture) -> None:
  mock_content = {
    "content": {
      "meta": {"id": "mock id", "text": "mock text"},
      "foo": "mock id",
      "bar": "baz",
    }
  }

  mock_file = mocker.mock_open(read_data="open file")
  mocker.patch("builtins.open", mock_file)
  mock_load = mocker.patch.object(json, "load", return_value=mock_content)
  mock_dump = mocker.patch.object(json, "dump")
  mocker.patch("shared.utils.FLOW_NAMES", return_value=["flow 1"])

  templatise()

  assert mock_load.call_args == [(mock_file.return_value,), {}]
  assert mock_dump.call_args == [
    (
      {
        "content": {
          "meta": {"id": "{{resources['MockText']}}", "text": "mock text"},
          "foo": "{{resources['MockText']}}",
          "bar": "baz",
        }
      },
      mock_file.return_value,
    ),
    {"indent": 2},
  ]
