from fastapi.testclient import TestClient
from fastapi import status
import pytest

from insights_content_template_renderer.endpoints import app
from insights_content_template_renderer.tests.utils_test import test_request_data, test_response_data


client = TestClient(app)

ENDPOINT__V1_RENDERED_REPORTS = "/v1/rendered_reports"

@pytest.mark.parametrize("method", [client.get, client.put, client.delete])
def test_bad_method(method):
    response = method(ENDPOINT__V1_RENDERED_REPORTS)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_no_data():
    response = client.post(ENDPOINT__V1_RENDERED_REPORTS)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_valid_data():
    response = client.post(ENDPOINT__V1_RENDERED_REPORTS, json=test_request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == test_response_data

