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
            self.redis.set_to_hash('sites', item['domain'], 0)

        link = item['link']
        link_domain = link.split('/')[2]
        if not self.redis.exists_in_hash('sites', link_domain):
            # set the value of the link domain to an empty list
            list_str = '[]'
            self.redis.set_to_hash('sites', link_domain, list_str)
        
        val = self.redis.get_from_hash('sites', link_domain)
        item_dict = ItemAdapter(item).asdict()
        if val:
            # append the link to the list
            val = json.loads(val)
            val.append(item_dict)
            val_str = json.dumps(val)
            self.redis.set_to_hash('sites', link_domain, val_str)
        else:
            # set the value of the link domain to a list with the link
            item_dict_list = [item_dict]
            self.redis.set_to_hash('sites', link_domain, json.dumps(item_dict_list))

        return item
