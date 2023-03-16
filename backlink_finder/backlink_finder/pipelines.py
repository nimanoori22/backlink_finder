# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .redisdb import RedisDB
import json

class BacklinkFinderPipeline:

    def __init__(self):
        self.redis = RedisDB('localhost', 6379, 0)

    def process_item(self, item, spider):
        if not self.redis.exists_in_hash('sites', item['domain']):
            self.redis.set_to_hash('sites', item['domain'], '[]')

        link = item['link']
        link_domain = link.split('/')[2]
        if not self.redis.exists_in_hash('sites', link_domain):
            self.redis.set_to_hash('sites', link_domain, '[]')
        
        val = self.redis.get_from_hash('sites', link_domain)
        try:
            val = json.loads(val)
        except json.decoder.JSONDecodeError:
            val = []
        item_dict = ItemAdapter(item).asdict()
        if len(val) > 0:
            val.append(item_dict)
            val_str = json.dumps(val)
            self.redis.set_to_hash('sites', link_domain, val_str)
        else:
            item_dict_list = [item_dict]
            self.redis.set_to_hash('sites', link_domain, json.dumps(item_dict_list))

        return item
