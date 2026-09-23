#!/usr/bin/env python3
"""Static preflight for generated, standalone explanation HTML."""

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path


class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.external = []
        self.labels = 0
        self.range_inputs = 0
        self.buttons = 0
        self.script_src = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if tag == "label":
            self.labels += 1
        if tag == "input" and attrs.get("type") == "range":
            self.range_inputs += 1
        if tag == "button":
            self.buttons += 1
        if tag == "script" and "src" in attrs:
            self.script_src += 1
        for key in ("src", "href", "action", "poster"):
            value = attrs.get(key, "")
            if value and not value.startswith("#"):
                self.external.append(f"{tag}[{key}]={value[:80]}")


def check(path):
    source = Path(path).read_text(encoding="utf-8")
    parser = Inspect()
    parser.feed(source)
    failures = []
    if not re.match(r"\s*<!doctype html\s*>", source, re.I):
        failures.append("missing HTML5 doctype")
    if not re.search(r"</html>\s*$", source, re.I):
        failures.append("missing closing html tag")
    if not ({"svg", "canvas"} & set(parser.tags)):
        failures.append("missing SVG or Canvas")
    if parser.range_inputs + parser.buttons == 0:
        failures.append("missing interactive control")
    if parser.range_inputs and not parser.labels:
        failures.append("range input has no label")
    if "script" not in parser.tags:
        failures.append("missing inline JavaScript")
    if parser.script_src or parser.external:
        failures.append("external dependency: " + ", ".join(parser.external or ["script src"]))
    if re.search(r"\b(?:fetch\s*\(|XMLHttpRequest\b|WebSocket\s*\(|import\s*\(|navigator\.sendBeacon\b)", source):
        failures.append("network or dynamic import call")
    if re.search(r"\b(?:TODO|REPLACE_ME|YOUR_API_KEY)\b", source):
        failures.append("unfinished placeholder")
    return {"ok": not failures, "failures": failures,
            "observed": {"range_inputs": parser.range_inputs,
                         "buttons": parser.buttons,
                         "svg": "svg" in parser.tags,
                         "canvas": "canvas" in parser.tags}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html_file")
    args = ap.parse_args()
    result = check(args.html_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
