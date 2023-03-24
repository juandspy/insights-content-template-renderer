import json
from pathlib import Path


example_request_data = {}
test_data_path = Path(__file__).with_name("data/request_data_example.json")
with test_data_path.open(encoding="UTF-8") as f:
    example_request_data = json.load(f)

example_response_data = {}
example_response_data = Path(__file__).with_name("data/response_data_example.json")
with example_response_data.open(encoding="UTF-8") as f:
    example_response_data = json.load(f)