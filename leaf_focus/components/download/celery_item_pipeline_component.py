import json

from itemadapter import ItemAdapter

from leaf_focus.components.download.spider import Spider
from leaf_focus.pipeline.tasks import pdf_identify


class CeleryItemPipelineComponent:
    def open_spider(self, spider: Spider):
        self._operations = spider.leaf_focus_operations

    def process_item(self, item, spider: Spider):
        adapter = ItemAdapter(item)

        # get the path to the details file
        pdf_file = adapter.get("path")
        details_file = self._operations.location.details_file(pdf_file)

        # save the details file
        details = adapter.asdict()
        with open(details_file, "wt") as f:
            json.dump(details, f)

        # call the pdf identify celery task
        base_dir = self._operations.base_dir
        pdf_identify.si(str(details_file), str(base_dir)).delay()
