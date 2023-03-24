import json


example_request_data = {}
with open("insights_content_template_renderer/data/request_data_example.json", encoding="UTF-8") as f:
    example_request_data = json.load(f)

example_response_data = {}
with open("insights_content_template_renderer/data/response_data_example.json", encoding="UTF-8") as f:
    example_response_data = json.load(f)

example_content_data = {}
with open("insights_content_template_renderer/data/content_example.json", encoding="UTF-8") as f:
    example_content_data = json.load(f)
