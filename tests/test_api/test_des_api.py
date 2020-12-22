from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

des_json_input = """{
  "processes": [
    {
      "name": "Pick",
      "duration": 1,
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
      "input_queues": [
        {
          "name": "ship_staging",
          "rate": {
            "type": "static",
            "static_value": 3
          }
        }
      ],
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
    "epochs": 100,
    "time_unit": "seconds"
  }
}"""


def test_des():
    response = client.post(
            "/discrete-event/run-simulation",
            headers={"Content-Type": "application/json"},
            json=des_json_input,
    )
