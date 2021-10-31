from dataclasses import dataclass, field

from base_test import BaseTest


class TestReportPage(BaseTest):
    def test_dataclass(self):
        @dataclass
        class Line:
            example: str
            page: "Page"

            @classmethod
            def load(cls, p: "Page"):
                yield Line(example="line example", page=p)

        @dataclass
        class Page:
            example: str
            doc: "Doc"
            lines: list[Line] = field(default_factory=list)

            @classmethod
            def load(cls, d: "Doc"):
                p = Page(example="testing", doc=d)
                lines = Line.load(p)
                p.lines = list(lines)
                yield p

        @dataclass
        class Doc:
            example: str
            pages: list[Page] = field(default_factory=list)

            @classmethod
            def load(cls):
                d = Doc(example="one")
                pages = Page.load(d)
                d.pages = list(pages)
                yield d

        doc = Doc(example="testing doc")
        assert doc.pages == []

        page = Page(example="testing page", doc=doc)
        assert page.lines == []

        line = Line(example="testing line", page=page)
