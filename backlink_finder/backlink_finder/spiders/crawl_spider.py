import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import BacklinkFinderItem
from ..redisdb import RedisDB
import json

class WebSpider(CrawlSpider):
    name = 'web_spider'
    start_urls = ['https://www.varzesh3.com/news/1871643/%D8%A7%D9%85%D8%B3%D8%A7%D9%84-%D9%86%D8%A7%D9%BE%D9%88%D9%84%DB%8C-%D8%AF%D8%B1-%DA%86%D9%85%D9%BE%DB%8C%D9%88%D9%86%D8%B2%D9%84%DB%8C%DA%AF-%D8%B7%D9%84%D8%B3%D9%85-%D8%B4%DA%A9%D9%86%DB%8C-%D9%85%DB%8C-%DA%A9%D9%86%D8%AF']
    deny_list = json.loads(RedisDB('localhost', 6379, 0).get('top_websites'))
    rules = (
        Rule(
        LinkExtractor(deny_domains=(deny_list)), 
        callback='parse', 
        follow=True,
        ),
    )

    def __init__(self, *args, **kwargs):

        super(WebSpider, self).__init__(*args, **kwargs)
        self.redis = RedisDB('localhost', 6379, 0)


    def parse(self, response):
        domain = response.url.split('/')[2]
        external_links = LinkExtractor(allow=(), deny=domain).extract_links(response)
        # external_links = [link for link in links if domain not in link.url]
        status = response.status
        page = response.url

        if not self.redis.exists_in_hash('sites', domain):
            self.redis.set_to_hash('sites', domain, '[]')

        for link in external_links:
            yield BacklinkFinderItem(
                page=page,
                link=link.url,
                domain=domain,
                status=status,
                nofollow=link.nofollow,
                keyword=link.text
            )
        
        # return response.follow_all(links, self.parse)


class TopWebsites(scrapy.Spider):
    name = 'top_websites'
    start_urls = ['https://www.expireddomains.net/alexa-top-websites/?#listing']

    def __init__(self, name=None, **kwargs):
        self.redis = RedisDB('localhost', 6379, 0)

    def parse(self, response):
        top_websites = response.css('td:nth-child(1) a::text').getall()
        
        if not self.redis.exists('top_websites'):
            self.redis.set('top_websites', json.dumps(top_websites))
        
        elif self.redis.exists('top_websites'):
            redis_top_websites = json.loads(self.redis.get('top_websites'))
            redis_top_websites.extend(top_websites)
            redis_top_websites = list(set(redis_top_websites))
            self.redis.set('top_websites', json.dumps(redis_top_websites))
        
        next = response.css('a.next::attr(href)').get()
        if next:
            if next == '/alexa-top-websites/?start=100#listing':
                return
            yield response.follow(next, self.parse)
