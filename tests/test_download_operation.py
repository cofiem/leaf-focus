import logging

from leaf_focus.download.crawl.operation import Operation


class TestDownloadOperation:
    def test_instance(self, tmp_path):
        feed_dir = tmp_path / "feed"
        cache_dir = tmp_path / "cache"
        Operation(logging.getLogger(), feed_dir, cache_dir)
