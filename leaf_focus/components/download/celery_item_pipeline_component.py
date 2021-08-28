import json

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from leaf_focus.components.download.spider import Spider
from leaf_focus.components.serialise import LeafFocusJsonEncoder
from leaf_focus.components.store.location import Location


class CeleryItemPipelineComponent:
    def process_item(self, item, spider: Spider):

        if not item:
            raise DropItem()

        from leaf_focus.pipeline.pdf.identify import pdf_identify

        adapter = ItemAdapter(item)

        # get the path to the details file
        pdf_file = adapter.get("path")
        location = Location(spider.logger)
        details_path = location.details_file(pdf_file)

        # save the details file
        details = adapter.asdict()
        with open(details_path, "wt") as f:
            json.dump(details, f, indent=2, cls=LeafFocusJsonEncoder)

        # call the pdf identify celery task
        pdf_identify.si(str(details_path)).delay()

        # return the item so it continues in the scrapy item pipeline
        return item
