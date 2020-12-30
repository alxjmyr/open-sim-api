import json

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

des_json_input = """{
  "processes": [
    {
      "name": "Pick",
      "duration": 1,
      "output_queue_selection": {
        "type": "all"
      },
      "output_queues": [
        {
          "name": "ship_staging",
          "rate": {
            "type": "static",
            "static_value": 3
          }
        }
      ]
    },
    {
      "name": "Ship",
      "duration": 1,
      "input_queue_selection": {
        "type": "all"
      },
      "input_queues": [
        {
          "name": "ship_staging",
          "rate": {
            "type": "static",
            "static_value": 3
          }
        }
      ],
      "output_queue_selection": {
        "type": "all"
      },
      "output_queues": [
        {
          "name": "shipped",
          "rate": {
            "type": "static",
            "static_value": 3
          }
        }
      ]
    }
  ],
  "queues": [
    {
      "name": "shipped",
      "capacity": 10000,
      "inital_value": 0,
      "queue_type": "continuous"
    },
    {
      "name": "ship_staging",
      "capacity": 200,
      "inital_value": 30,
      "queue_type": "continuous"
    }
  ],
  "sim_def": {
    "name": "Pick and Ship Simulation",
    "epochs": 25,
    "time_unit": "seconds"
  }
}"""


def test_des():
    """
    High level test of DES endpoint functionality
    :return:
    """
    response = client.post(
            "/discrete-event/run-simulation",
            headers={"Content-Type": "application/json"},
            json=json.loads(des_json_input),
    )

    data = response.json()

    assert response.status_code == 201

    assert "process_output" in data.keys()
    assert type(data['process_output']) == list
    assert len(data['process_output']) == 46

    assert "queue_output" in data.keys()
    assert type(data['queue_output']) == list
    assert len(data['queue_output']) == 50

    assert "resource_output" in data.keys()
    assert type(data["resource_output"]) == list
    assert len(data["resource_output"]) == 0

    assert "sim_def" in data.keys()
    assert type(data['sim_def']) == dict
    assert len(data['sim_def']) == 3
