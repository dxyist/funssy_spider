# -*- coding: utf-8 -*-
import scrapy
from scrapy import log
from scrapy.http import FormRequest
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re



class Bc3tsSpider(CrawlSpider):
    name = "bc3ts"
    # allowed_domains = ["http://www.bc3ts.com/"]
    start_urls = ['http://http://www.bc3ts.com//']
    base_url = 'http://www.bc3ts.com'
    scan_limit = 100
    download_delay = 1

    def start_requests(self):
        categories = {
            u"首页": "",
            u"爆料公社": "1",
            u"報廢專區": "61",
            u"抱怨公社": "181",
            u"爆笑公社": "161",
            u"亞洲公社": "201",
            u"爆系故事館": "141",
            u"愛恨情仇": "21",
            u"美顏美妝": "101",
            u"旅遊美食": "81",
            u"小便碎碎念": "121",
        }
        # 页面从1开始
        url = 'http://www.bc3ts.com/category/categoryList?id=%s&page=%d' % (categories[u'爆料公社'], 1)
        yield Request(url, meta={'category_number': categories[u'爆料公社'], 'index': 1},
                      callback=self.page)  # simulate login request

        # test_url = 'http://www.bc3ts.com/post/1040'
        # yield Request(test_url, callback=self.article)  # simulate login request

    def page(self, response):
        # 尾递归
        bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        items = bs.find_all("div", class_="col-md-4")

        if len(items) == 0:
            print("item == empty")
            return
        scan_times = 0
        for item in items:
            # print(item)
            if scan_times >= self.scan_limit:
                return
            scan_times += 1
            page_url = re.findall("'(/post/\d+)'", item.find('div', class_="card mb-4")['onclick'])[0]
            doc_id = re.findall("\d{0,9}$", page_url)[0]
            time_str = str(item.find('small', class_="card-text").text).strip() + ':00'
            print(time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M:%S")))

            url = self.base_url + page_url
            yield Request(url, meta={'doc_id': doc_id, 'time': time}, callback=self.article)  # simulate login request
        category_number = response.meta['category_number']
        index = response.meta['index']
        if index > 10:
            return
        # if index > 10:
        #     return
        url = 'http://www.bc3ts.com/category/categoryList?id=%s&page=%d' % (category_number, index + 1)
        yield Request(url, meta={'category_number': category_number, 'index': index + 1},
                      callback=self.page)  # simulate login request

        pass

    def article(self, response):
        raw = {}
        bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        content_field = bs.find('div', class_='post-html')
        if len(content_field.find_all('iframe')) != 0:
            print(u"发现player视频页面!!!!!!")
            print(response.url)
            print('')
            return

        raw['title'] = bs.find('div', class_='post-title').h1.text

        raw['html'] = response.body
        raw['source_url'] = response.url
        raw['subtitle'] = 'bc3ts'

        raw['doc_id'] = response.meta['doc_id']
        raw['time'] = response.meta['time']

        content_ps = bs.find('div', class_='post-html').find_all({'div'})
        raw['content'] = []
        for p in content_ps:
            image = p.find('img')
            if image:
                image_content = {'text': '', 'image': image['src']};
                if image_content not in raw['content']:
                    raw['content'].append(image_content)
                    # print({'text': '', 'image': image['src']})

            else:
                raw['content'].append({'text': p.text.replace(u'\xa0', '').replace(u'\u3000', '').replace(u'\u200e', '')})
                # print({'text': p.text.replace('\xa0', '').replace('\u3000', '').replace('\u200e', '')})

        print(raw['title'])
        print(raw['source_url'])
        print(raw['subtitle'])
        print(raw['doc_id'])
        print(raw['time'])
        print(raw['content'])
        print('')

        pass

    def get_title_from_raw(self, raw):
        return raw['title']

    def get_subtitle_from_raw(self, raw):
        return raw['subtitle']

    def get_doc_id_from_raw(self, raw):
        return raw['doc_id']

    def get_source_url_from_raw(self, raw):
        return raw['source_url']

    def get_content_from_raw(self, raw):
        return raw['content']

    def get_time_from_raw(self, raw):
        return raw['time']

    def get_html_from_raw(self, raw):
        return ''
