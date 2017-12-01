# -*- coding: utf-8 -*-
import scrapy
from scrapy import log
from scrapy.http import FormRequest
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import json
import re
import hashlib


class AlarabiyaSpider(scrapy.Spider):
    name = 'alarabiya'
    # allowed_domains = ['http://www.alarabiya.net']
    # start_urls = ['http://http://www.bbc.com/arabic/middleeast/']
    base_url = u'http://www.alarabiya.net'
    download_delay = 0

    def start_requests(self):
        categories = {
            "medicine-and-health": u"健康",
            "technology": u"科技",
            "culture-and-art": u"文化",
            # "science": u"",
            "sport": u"体育",
            "arab-and-world/gulf": u"社会",
            "arab-and-world/egypt": u"社会",
            "arab-and-world/syria": u"社会",
            "iran": u"社会",
            "arab-and-world/yemen": u"社会",
            "arab-and-world/iraq": u"社会",
            # u"视频": "magazine",
        }

        # # 页面从1开始
        # url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % ('arab-and-world/yemen', 1)
        # yield Request(url, meta={'category_name': 'arab-and-world/yemen', 'index': 1},
        #               callback=self.page)  # simulate login request

        for category in categories:
            url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % (category, 1)
            yield Request(url, meta={'tag': categories[category], 'category_name': category, 'index': 1},
                          callback=self.page)  # simulate login request

        # test_url = 'http://www.alarabiya.net/ar/medicine-and-health/2017/11/26/%D9%87%D9%84-%D9%8A%D8%AA%D8%B3%D8%A8%D8%A8-%D8%AA%D8%B1%D9%85%D8%A8-%D9%81%D9%8A-%D8%B2%D9%8A%D8%A7%D8%AF%D8%A9-%D8%A3%D8%B9%D8%AF%D8%A7%D8%AF-%D8%A7%D9%84%D9%85%D8%B5%D8%A7%D8%A8%D9%8A%D9%86-%D8%A8%D8%A7%D9%84%D9%85%D9%84%D8%A7%D8%B1%D9%8A%D8%A7%D8%9F.html'
        # yield Request(test_url, callback=self.article)  # simulate login request
        pass

    def page(self, response):
        bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        items = bs.find_all("div", class_="item")
        if len(items) == 0:
            print("item == empty")
            return
        for item in items:
            title = item.find('a', class_='highline').text
            # subtitle = item.find('p', class_='eagle-item__summary').text
            create_time = item.find('div', class_='date').text
            page_url = self.base_url + item.find('a')['href']
            doc_id = (hashlib.md5(page_url.encode("utf8")).hexdigest())
            tag = response.meta['tag']
            meta = {'doc_id': doc_id,
                    'title': title,
                    'tag': tag,
                    # 'subtitle': subtitle,
                    'page_url': page_url,
                    'create_time': create_time}
            yield Request(page_url, meta=meta, callback=self.article)  # simulate login request

        category_name = response.meta['category_name']
        index = response.meta['index']
        print("index:", index)
        # if index > 100:
        #     return
        url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % (category_name, index + 1)
        yield Request(url, meta={'category_name': category_name, 'tag': tag, 'index': index + 1},
                      callback=self.page)  # simulate login request

    def article(self, response):
        raw = {}
        bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        #
        content_field = bs.find("article", class_="multi_articles")
        if content_field is None or len(content_field.find_all('video')) != 0:
            print(u"发现player视频页面!!!!!!")
            print(response.url)
            print('')
            return

        if len(content_field.find_all("div", class_="article-default-image is-video")) != 0:
            print(u"发现youtube视频页面!!!!!!")
            print(response.url)
            print('')
            return

        raw['title'] = response.meta['title']
        # raw['html'] = response.body
        raw['source_url'] = response.url
        raw['subtitle'] = 'alarabiya'
        raw['raw_tags'] = [response.meta['tag']]
        raw['doc_id'] = response.meta['doc_id']
        raw['time'] = response.meta['create_time']
        raw['content'] = []

        # 先存第一张图
        title_img = content_field.find('div', class_='article_img')
        image = title_img.find('img')
        if image:
            image_content = {'text': '', 'image': image['src']};
            if image_content not in raw['content']:
                raw['content'].append(image_content)
                # print({'text': '', 'image': image['src']})

        content_ps = content_field.find('div', class_='article-body').find_all({'p', 'figure'})
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
        # print(raw['source_url'])
        print(raw['subtitle'])
        print(raw['raw_tags'])
        print(raw['doc_id'])
        print(raw['time'])
        print(raw['content'])
        with open('bbc_message_full.txt', 'a') as f:
            f.write(json.dumps(raw) + '\n')

        pass
