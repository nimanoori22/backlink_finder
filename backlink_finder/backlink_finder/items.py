# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BacklinkFinderItem(scrapy.Item):
    page = scrapy.Field()
    link = scrapy.Field()
    domain = scrapy.Field()
    status = scrapy.Field()
    nofollow = scrapy.Field()
    keyword = scrapy.Field()
