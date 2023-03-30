# MIT License
#
# Copyright (c) 2022 David Chen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module implements the DoT.js template framework in Python.
Source: https://github.com/lucemia/doT
"""

import re

version = "1.0.0"

DEFAULT_TEMPLATE_SETTINGS = {
    "evaluate": r"\{\{([\s\S]+?\}?)\}\}",
    "interpolate": r"\{\{=([\s\S]+?)\}\}",
    "encode": r"\{\{!([\s\S]+?)\}\}",
    "use": r"\{\{#([\s\S]+?)\}\}",
    "useParams": r"(^|[^\w$])def(?:\.|\[[\'\"])([\w$\.]+)(?:[\'\"]\])?\s*\:\s*([\w$\.]+|\"["
    r"^\"]+\"|\'[^\']+\'|\{[^\}]+\})",
    "define": r"\{\{##\s*([\w\.$]+)\s*(\:|=)([\s\S]+?)#\}\}",
    "defineParams": r"^\s*([\w$]+):([\s\S]+)",
    "conditional": r"\{\{\?(\?)?\s*([\s\S]*?)\s*\}\}",
    "iterate": r"\{\{~\s*(?:\}\}|([\s\S]+?)\s*\:\s*([\w$]+)\s*(?:\:\s*([\w$]+))?\s*\}\})",
    "varname": "it",
    "strip": True,
    "append": True,
    "selfcontained": False,
}


class Renderer:
    """Class encapsulating logic of rendering DoT.js templates."""

    def __init__(self, template_settings=None):

        self.template_settings = template_settings
        if self.template_settings is None:
            self.template_settings = DEFAULT_TEMPLATE_SETTINGS

        self.startend = {
            "append": {
                "start": "'+(",
                "end": ")+'",
                "endencode": "||'').toString().encodeHTML()+'",
            },
            "split": {
                "start": "';out+=(",
                "end": ");out+='",
                "endencode": "||'').toString().encodeHTML();out+='",
            },
        }

        self.skip = "$^"

    def resolve_defs(self, c, tmpl, _def):
        # ignore the pre compile stage because we use it as backend translate.

        return tmpl

    def unescape(self, code):
        return re.sub(r"[\r\t\n]", " ", re.sub(r"\\(['\\])", r"\1", code))

    def _interpolate(self, code, cse):
        return cse["start"] + self.unescape(code) + cse["end"]

    def _encode(self, code, cse):
        return cse["start"] + self.unescape(code) + cse["endencode"]

    def _conditional(self, elsecode, code):
        if elsecode:
            if code:
                return "';}else if(" + self.unescape(code) + "){out+='"
            else:
                return "';}else{out+='"
        else:
            if code:
                return "';if(" + self.unescape(code) + "){out+='"
            else:
                return "';}out+='"

    def _iterate(self, iterate, vname, iname):
        if not iterate or not vname:
            return "';} } out+='"

        self.sid += 1
        indv = iname or "i" + str(self.sid)
        iterate = self.unescape(iterate)

        _sid = str(self.sid)
        #        print iterate, vname, iname, _sid

        return (
            "';var arr"
            + _sid
            + "="
            + iterate
            + ";if(arr"
            + _sid
            + "){var "
            + vname
            + ","
            + indv
            + "=-1,l"
            + _sid
            + "=arr"
            + _sid
            + ".length-1;while("
            + indv
            + "<l"
            + _sid
            + "){"
            + vname
            + "=arr"
            + _sid
            + "["
            + indv
            + "+=1];out+='"
        )

    def _evalute(self, code):
        return "';" + self.unescape(code) + "out+='"

    def template(self, tmpl, c=None, _def=None):
        c = c or self.template_settings
        #    needhtmlencode = None
        self.sid = 0
        #    indv = None

        cse = self.startend["append"] if c["append"] else self.startend["split"]

        _str = self.resolve_defs(c, tmpl, _def or {}) if (c["use"] or c["define"]) else tmpl

        if c.get("strip"):
            # remove white space
            _str = re.sub(r"(^|\r|\n)\t* +| +\t*(\r|\n|$)", " ", _str)
            _str = re.sub(r"\r|\n|\t|/\*[\s\S]*?\*/", "", _str)

        _str = re.sub(r"('|\\)", r"\\\1", _str)

        if c.get("interpolate"):
            _str = re.sub(c["interpolate"], lambda i: self._interpolate(i.groups()[0], cse), _str)

        if c.get("encode"):
            _str = re.sub(c["encode"], lambda i: self._encode(i.groups()[0], cse), _str)

        if c.get("conditional"):
            _str = re.sub(
                c["conditional"], lambda i: self._conditional(i.groups()[0], i.groups()[1]), _str
            )

        if c.get("iterate"):
            _str = re.sub(
                c["iterate"],
                lambda i: self._iterate(i.groups()[0], i.groups()[1], i.groups()[2]),
                _str,
            )

        if c.get("evaluate"):
            _str = re.sub(c["evaluate"], lambda i: self._evalute(i.groups()[0]), _str)

        return (
            "function anonymous(" + c["varname"] + ") {var out='" + _str + "';return out;}"
        )