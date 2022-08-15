import js2py

from insights_content_template_renderer import DoT
from insights_content_template_renderer.DoT import template_settings


DoT_settings = template_settings


def test_single_quote_correct_handling():
    """
    Checks that DoT template function escapes single quotes
    before creating a JS function out of them.
    """
    template = "An OCP node behaves unexpectedly when it doesn't meet the minimum resource requirements"
    text = js2py.eval_js(DoT.template(template, DoT_settings))()
    assert text == "An OCP node behaves unexpectedly when it doesn't meet the minimum resource requirements"
