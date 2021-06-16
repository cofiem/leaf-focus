# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LeafFocusItem(scrapy.Item):
    name = scrapy.Field()
    category = scrapy.Field()
    path = scrapy.Field()
    url = scrapy.Field()
    referrer = scrapy.Field()
    last_updated = scrapy.Field()
