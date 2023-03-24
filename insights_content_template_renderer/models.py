from typing import List, Dict
import uuid

from pydantic import BaseModel

from insights_content_template_renderer.data import \
        example_request_data, example_response_data


class Content(BaseModel):
    plugin: dict
    error_keys: dict
    generic: str
    summary: str
    resolution: str
    more_info: str
    reason: str
    HasReason: bool

    class Config:
        schema_extra = {
            "example": {
                "plugin": {
                        "name": "",
                        "node_id": "",
                        "product_code": "",
                        "python_module": "rule_1"
                },
                "error_keys": {
                        "RULE_1": {
                                "metadata": {
                                        "description": "rule 1 error key description",
                                        "impact": {
                                                "name": "impact_1",
                                                "impact": 3
                                        },
                                        "likelihood": 2,
                                        "publish_date": "",
                                        "status": "",
                                        "tags": None
                                },
                                "total_risk": 0,
                                "generic": "",
                                "summary": "",
                                "resolution": "",
                                "more_info": "",
                                "reason": "rule 1 reason",
                                "HasReason": True
                        },
                        "RULE_2": {
                                "metadata": {
                                        "description": "rule 2 error key description",
                                        "impact": {
                                                "name": "impact_2",
                                                "impact": 2
                                        },
                                        "likelihood": 3,
                                        "publish_date": "",
                                        "status": "",
                                        "tags": None
                                },
                                "total_risk": 0,
                                "generic": "",
                                "summary": "",
                                "resolution": "",
                                "more_info": "",
                                "reason": "",
                                "HasReason": False
                        }
                },
                "generic": "",
                "summary": "rule 1 summary",
                "resolution": "rule 1 resolution",
                "more_info": "rule 1 more info",
                "reason": "rule 1 reason",
                "HasReason": True
            }
        }


class Report(BaseModel):
    type: str
    component: str
    key: str
    details: dict

    class Config:
        schema_extra = {
            "example": {
                "type": "rule",
                "component": "rule.report",
                "key": "RULE",
                "details": {}
            }
        }

class ReportPerCluster(BaseModel):
    reports: List[Report]

class RenderedReport(BaseModel):
	rule_id: str
	error_key: str
	resolution: str
	reason: str
	description: str

class ReportData(BaseModel):
    clusters: List[str]
    reports: Dict[str, ReportPerCluster]

    class Config:
        schema_extra = {
            "example": {
                "clusters": [
                        "e1a379e4-9ac5-4353-8f82-ad066a734f18"
                ],
                "reports": {
                        "e1a379e4-9ac5-4353-8f82-ad066a734f18": {
                                "reports": [
                                        {
                                                "type": "rule",
                                                "component": "rule_1.report",
                                                "key": "RULE_1",
                                                "details": {}
                                        },
                                        {
                                                "type": "rule",
                                                "component": "rule_2.report",
                                                "key": "RULE_2",
                                                "details": {}
                                        }
                                ]
                        }
                }
            }
        }

class RendererRequest(BaseModel):
    content: List[Content]
    report_data: ReportData

    class Config:
        schema_extra = {
            "example": example_request_data
        }

class RendererResponse(BaseModel):
    clusters: List[str]
    reports: Dict[str, List[RenderedReport] ]

    class Config:
        schema_extra = {
            "example": example_response_data
        }
