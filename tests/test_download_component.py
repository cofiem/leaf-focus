import logging
from pathlib import Path

import pytest

from leaf_focus.download.crawl.component import Component
from leaf_focus.download.crawl.item import Item
from tests.base_test import BaseTest


class TestDownloadComponent(BaseTest):

    example_domain = "aph.gov.au"
    example_url = "https://www.aph.gov.au/Parliamentary_Business/Chamber_documents/HoR/Order_of_Business"

    def test_instance(self, tmp_path):
        feed_dir = tmp_path / "feed"
        cache_dir = tmp_path / "cache"
        Component(logging.getLogger(), feed_dir, cache_dir)

    @pytest.mark.slow
    def test_run(self, caplog, tmp_path, exe_pdf_image):
        caplog.set_level(logging.INFO)

        feed_dir = tmp_path / "feed"
        cache_dir = tmp_path / "cache"
        c = Component(logging.getLogger(), feed_dir, cache_dir)

        url = {"category": "default", "url": self.example_url, "comment": None}
        c.run([self.example_domain], [url])

        assert caplog.record_tuples[-1] == (
            "scrapy.core.engine",
            20,
            "Spider closed (finished)",
        )
        assert len(caplog.record_tuples) == 19

        feed_path = list(feed_dir.glob("*.csv"))[0]
        feed_items = list(Item.load(feed_path))

        assert len(feed_items) == 2
        assert feed_items[0].name.startswith("House Order of Business")
        assert feed_items[1].name.startswith("Federation Chamber Order of Business")
