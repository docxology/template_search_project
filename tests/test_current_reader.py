"""Check citation and resource targets in the checked-in current HTML reader."""

import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = Counter()
        self.citations = set()
        self.assets = set()
        self.entry_text = set()
        self.entry = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        identifier = attributes.get("id", "")
        self.ids[identifier] += 1
        if identifier.startswith("ref-"):
            self.entry = identifier
        href = attributes.get("href", "")
        if tag == "a" and href.startswith("#ref-"):
            self.citations.add(unquote(href[1:]))
        if tag in {"img", "script", "link"}:
            source = urlsplit(attributes.get("src", attributes.get("href", "")))
            if source.path and not (source.scheme or source.netloc):
                self.assets.add(unquote(source.path))

    def handle_endtag(self, tag):
        if tag == "div":
            self.entry = None

    def handle_data(self, data):
        if self.entry and data.strip():
            self.entry_text.add(self.entry)


def test_current_reader_resolves_standard_and_deep_citations():
    docs = Path(__file__).resolve().parents[1] / "docs"
    path = docs / "reader/web/index.html"
    manuscript = docs / "manuscript"
    reader = Reader()
    reader.feed(path.read_text(encoding="utf-8"))
    reader.close()

    standard_bib = (manuscript / "references.bib").read_text(encoding="utf-8")
    deep_bib = (manuscript / "references_deep.bib").read_text(encoding="utf-8")
    key_pattern = r"@[A-Za-z]+\s*\{\s*([^,\s]+)"
    standard_keys = set(re.findall(key_pattern, standard_bib))
    deep_keys = set(re.findall(key_pattern, deep_bib))
    supplement = (manuscript / "S01_literature_review.md").read_text(encoding="utf-8")
    cited_deep = set(re.findall(r"@([\w:.-]+)", supplement)) & deep_keys

    assert standard_keys and cited_deep
    assert {f"ref-{key}" for key in standard_keys | cited_deep} <= reader.citations
    assert reader.citations <= reader.entry_text
    assert all(reader.ids[target] == 1 for target in reader.citations)
    assert all((path.parent / asset).is_file() for asset in reader.assets)
