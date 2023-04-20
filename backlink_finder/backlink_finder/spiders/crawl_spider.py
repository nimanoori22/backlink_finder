import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import BacklinkFinderItem
from ..redisdb import RedisDB
import json
from urllib.parse import urlparse

class WebSpider(CrawlSpider):
    name = 'web_spider'
    start_urls = ['https://www.wikipedia.org/']
    try:
        deny_list = json.loads(RedisDB('localhost', 6379, 0).get('top_websites'))
    except TypeError:
        deny_list = []
    rules = (
        Rule(
        LinkExtractor(allow=()),
        callback='parse', 
        follow=True,
        ),
    )

    def __init__(self, *args, **kwargs):

        super(WebSpider, self).__init__(*args, **kwargs)
        self.redis = RedisDB('localhost', 6379, 0)


    def parse(self, response):
        url = urlparse(response.url)
        domain = f'{url.scheme}://{url.netloc}'
        external_links = LinkExtractor(allow=(), deny=domain).extract_links(response)
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


class TopWebsites(scrapy.Spider):
    name = 'top_websites'
    start_urls = ['https://www.expireddomains.net/alexa-top-websites/?#listing']

    def __init__(self, name=None, **kwargs):
        self.redis = RedisDB('localhost', 6379, 0)

    def parse(self, response):
        top_websites = response.css('td:nth-child(1) a::text').getall()
        if 'wikipedia.org' in top_websites:
            top_websites.remove('wikipedia.org')
        
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
