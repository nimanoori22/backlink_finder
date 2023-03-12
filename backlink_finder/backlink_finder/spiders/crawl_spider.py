import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import BacklinkFinderItem
from ..redisdb import RedisDB

class WebSpider(scrapy.Spider):
    name = 'web_spider'
    start_urls = ['https://www.varzesh3.com/news/1871643/%D8%A7%D9%85%D8%B3%D8%A7%D9%84-%D9%86%D8%A7%D9%BE%D9%88%D9%84%DB%8C-%D8%AF%D8%B1-%DA%86%D9%85%D9%BE%DB%8C%D9%88%D9%86%D8%B2%D9%84%DB%8C%DA%AF-%D8%B7%D9%84%D8%B3%D9%85-%D8%B4%DA%A9%D9%86%DB%8C-%D9%85%DB%8C-%DA%A9%D9%86%D8%AF']

    def __init__(self, *args, **kwargs):

        super(WebSpider, self).__init__(*args, **kwargs)
        self.redis = RedisDB('localhost', 6379, 0)


    def parse(self, response):
        links = LinkExtractor().extract_links(response)
        domain = response.url.split('/')[2]
        external_links = [link for link in links if domain not in link.url]
        status = response.status
        page = response.url

        if not self.redis.exists_in_hash('sites', domain):
            self.redis.set_to_hash('sites', domain, 0)

        for link in external_links:
            yield BacklinkFinderItem(
                page=page,
                link=link.url,
                domain=domain,
                status=status,
                nofollow=link.nofollow,
                keyword=link.text
            )
        
        # for link in links:
        #     yield response.follow(link.url, callback=self.parse)


        