# -*- coding: utf-8 -*-
import scrapy
from scrapy import log
from scrapy.http import FormRequest
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from bs4 import BeautifulSoup


class FunssySpider(scrapy.Spider):
    name = "funssy"
    allowed_domains = ["www.funssy.com"]
    start_urls = ['http://www.funssy.com/']
    base_url = 'http://www.funssy.com'
    # scan_limit = 30
    download_delay = 1

    # Scrapy will call this function at first
    def start_requests(self):
        categories = {
            u"首页": "",

            u"时事新闻": "30",
            u"娱乐新闻": "2",
            u"感动温馨": "6",

            u"搞笑大全": "1",
            u"有趣资讯": "13",
            u"内涵漫画": "27",

            u"生活达人": "11",
            u"美食天堂": "29",
            u"旅游资讯": "22",
            u"健康医疗": "21",
            u"运动体育": "19",
            u"爱情语录": "5",
            u"美容衣饰": "10",

            u"动漫世界": "9",
            u"酷爆科技": "20",
            u"星座运程": "23",
            u"命理玄机": "25",
            u"宠物资讯": "24",

            u"奇闻怪事": "18",
            u"灵异恐怖": "3",
            # u"恐怖漫画": "28",
        }

        url = 'http://www.funssy.com/ajax_index.aspx?pageIndex=%d&typeID=%s' % (0, categories['时事新闻'])
        # yield Request(url, meta={'category_number': categories['时事新闻'], 'index': 0}, callback=self.page)  # simulate login request

        test_url = 'http://www.funssy.com/article/3/ln4D5Vfm.html'
        yield Request(test_url, callback=self.article)  # simulate login request

    def page(self, response):

        # 尾递归
        bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        items = bs.find_all("div", class_="item")
        if len(items) == 0:
            return
        # scan_times = 0
        for item in items:
            # if scan_times >= self.scan_limit:
            #     return
            # scan_times += 1
            url = self.base_url + item.find('a')['href']
            yield Request(url, callback=self.article)  # simulate login request
        category_number = response.meta['category_number']
        index = response.meta['index']
        print("index:", index)
        if index > 10:
            return
        url = 'http://www.funssy.com/ajax_index.aspx?pageIndex=%d&typeID=%s' % (index + 1, category_number)
        yield Request(url, meta={'category_number': category_number, 'index': index + 1},
                      callback=self.page)  # simulate login request

    def article(self, response):
        raw = {}
        bs = BeautifulSoup(response.body, 'lxml')
        content_field = bs.find('div', class_='div_object_desc')
        if len(content_field.find_all('iframe')) != 0:
            print("发现iframe视频页面!!!!!!")
            print(response.url)
            return
        if len(bs.find_all('blockquote', class_='instagram-media')) != 0:
            print("发现instagram视频页面!!!!!!")
            print(response.url)
            return

        #
        # if len(bs.find_all('div', id='player')) != 0:
        #     print("发现player视频页面!!!!!!")
        #     print(response.url)
        #     return


        raw['title'] = bs.find('div', class_='contentBox').h1.text
        raw['html'] = response.body
        raw['source_url'] = response.url
        raw['subtitle'] = 'funssy'
        print(raw['title'])
        content_ps = bs.find('div', class_='div_object_desc').find_all({'p', 'h3'})
        raw['content'] = []
        for p in content_ps:
            image = p.find('img')
            if image:
                raw['content'].append({'text': '', 'image': image['src']})
                print({'text': '', 'image': image['src']})
            else:
                raw['content'].append({'text': p.text.replace('\xa0','')})
                print({'text': p.text.replace('\xa0','')})

        # print(raw['content'])
        #
        # print(raw['images'])
        pass
