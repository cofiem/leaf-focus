import json

from itemadapter import ItemAdapter

from leaf_focus.components.download.spider import Spider
from leaf_focus.components.store.location import Location


class CeleryItemPipelineComponent:
    def process_item(self, item, spider: Spider):

        from leaf_focus.pipeline.pdf.identify import pdf_identify

        adapter = ItemAdapter(item)

        # get the path to the details file
        pdf_file = adapter.get("path")
        location = Location(spider.logger)
        details_file = location.details_file(pdf_file)

        # save the details file
        details = adapter.asdict()
        with open(details_file, "wt") as f:
            json.dump(details, f)

        # call the pdf identify celery task
        base_dir = spider.leaf_focus_config.pdf_base_dir
        pdf_identify.si(str(details_file), str(base_dir)).delay()
