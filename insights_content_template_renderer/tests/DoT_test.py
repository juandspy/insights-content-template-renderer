import js2py

from insights_content_template_renderer import DoT
from insights_content_template_renderer.DoT import DEFAULT_TEMPLATE_SETTINGS


DoT_settings = DEFAULT_TEMPLATE_SETTINGS
renderer = DoT.Renderer()


def test_single_quote_correct_handling():
    """
    Checks that DoT template function escapes single quotes
    before creating a JS function out of them.
    """
    template = "An OCP node behaves unexpectedly when it doesn't meet the minimum resource requirements"
    text = js2py.eval_js(renderer.template(template, DoT_settings))()
    assert (
        text
        == "An OCP node behaves unexpectedly when it doesn't meet the minimum resource requirements"
    )


def test_nonletter_characters_correct_handling():
    """
    Checks that DoT.template function does not remove characters like
    escape characers and single quotes from the given input if strip is
    set to False
    """
    input = r"Red Hat recommends that you configure your nodes to meet the minimum resource requirements.\n\nMake " \
            r"sure that:\n\n1. Node foo1 (undefined) * Has enough memory, minimum requirement is 16. Currently its " \
            r"only configured with 8.16GB. "

    text = js2py.eval_js(renderer.template(input, DoT_settings._replace(strip = False)))()
    assert text == input

def test_CCXDEV_10314():
    """Check that CCXDEV-10314 has been solved and newlines aren't an issue."""
    INPUT = "{{?pydata.options == 1\n}}Option 1{{?? pydata.options == 2\n}}Option 2{{??\n}}Other option{{?}}:\n\nMore text"
    want = """function anonymous(pydata) {var out='';if(pydata.options == 1){out+='Option 1';}else if(pydata.options == 2){out+='Option 2';}else{out+='Other option';}out+=':

More text';return out;}"""
    
    settings = DEFAULT_TEMPLATE_SETTINGS
    out = renderer.template(INPUT, settings._replace(strip = False))

    assert out == want
