# -*- coding: utf-8 -*-
import scrapy
from scrapy import log
from scrapy.http import FormRequest
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re

class BbcArabicSpider(scrapy.Spider):
    name = 'bbc_arabic'
    #allowed_domains = ['http://www.bbc.com/']
    start_urls = ['http://http://www.bbc.com/arabic/middleeast/']
    base_url = 'http://www.bbc.com'
    def start_requests(self):
        categories = {
            u"首页": "",
            u"中东新闻": "middleeast",
            u"世界新闻": "world",
            u"科技": "scienceandtech",
            u"健康": "topics/c4794229-7f87-43ce-ac0a-6cfcd6d3cef2",
            u"经济": "business",
            u"文化艺术": "artandculture",
            u"体育": "sports",
            u"杂志": "magazine",
            u"女性": "topics/e45cb5f8-3c87-4ebd-ac1c-058e9be22862",
            #u"视频": "magazine",

        }
        # 页面从1开始
        url = 'http://www.bbc.com/arabic/%s' % (categories[u'文化艺术'])
        yield Request(url, meta={'category_number': categories[u'文化艺术']},
                      callback=self.page)  # simulate login request

        # test_url = 'http://www.bc3ts.com/post/1040'
        # yield Request(test_url, callback=self.article)  # simulate login request

    def page(self, response):
        bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        items = bs.find_all("div", class_="eagle-item faux-block-link")
        if len(items) == 0:
            print("item == empty")
            return
        # scan_times = 0
        for item in items:
            title = item.find('h3', class_='title-link__title').text
            subtitle = item.find('p', class_='eagle-item__summary').text
            create_time = item.find('li', class_='mini-info-list__item').text
            page_url = self.base_url + item.find('a')['href']
            doc_id = re.findall("\d{0,9}$", item.find('a')['href'])[0]
            meta = {'doc_id': doc_id, 'title': title, 'subtitle': subtitle,'page_url': page_url,'create_time': create_time}
            yield Request(page_url, meta=meta, callback=self.article)  # simulate login request

    def article(self, response):
        print('article')
        raw = {}
        bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        content_field = bs.find('div', class_='story-body__inner')
        # 存在只有视频的页面，这种页面没有 'story-body__inner' 的 div
        if content_field is None or len(content_field.find_all('figure',class_='media-with-caption')) != 0:
            print(u"发现player视频页面!!!!!!")
            print(response.url)
            print('')
            return

        raw['title'] = response.meta['title']

        raw['html'] = response.body
        raw['source_url'] = response.url
        raw['subtitle'] = 'bbc_arabic'

        raw['doc_id'] = response.meta['doc_id']
        raw['time'] = response.meta['create_time']
        #
        content_ps = bs.find('div', class_='story-body__inner').find_all({'p', 'figure'})
        raw['content'] = []
        for p in content_ps:
            image = p.find('img')
            if image:
                image_content = {'text': '', 'image': image['src']};
                if image_content not in raw['content']:
                    raw['content'].append(image_content)
                    # print({'text': '', 'image': image['src']})

            else:
                raw['content'].append(
                    {'text': p.text.replace(u'\xa0', '').replace(u'\u3000', '').replace(u'\u200e', '')})
                # print({'text': p.text.replace('\xa0', '').replace('\u3000', '').replace('\u200e', '')})

        print(raw['title'])
        print(raw['source_url'])
        print(raw['subtitle'])
        print(raw['doc_id'])
        print(raw['time'])
        print(raw['content'])
        # print('')

        pass