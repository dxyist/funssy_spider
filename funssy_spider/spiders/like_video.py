# -*- coding: utf-8 -*-
import scrapy
from scrapy import log
from scrapy.http import FormRequest
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import requests
import time
import json
import re
import hashlib
from ..feeds_back_utils import *
import cv2.cv as cv


class LikeSpider(scrapy.Spider):
    name = 'like'
    # allowed_domains = ['http://www.alarabiya.net']
    # start_urls = ['http://http://www.bbc.com/arabic/middleeast/']
    base_url = u'http://www.alarabiya.net'
    download_delay = 0
    hd = {'pragma': 'no-cache',
          'cache-control': 'no-cache'}
    page = 0
    max_page = 30
    # channel_list = get_channel_list('like', 'Thailand')
    channel_list = [
        # 'https://like.video/live/share/profile?c=cp&b=56983047&l=zh-Hans&t=1',
        'https://like.video/live/share/profile?c=cp&b=53334870&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=58196898&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=61601683&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=56801797&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=64239159&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=62785504&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=53300227&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=55835496&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=64150727&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=56692193&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=58415676&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=53290532&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=62520040&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=53676402&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=53676402&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=59309357&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=59687631&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=59792985&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=64972779&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=58471066&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=58833035&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=59087239&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=56367900&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=58508470&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=56417667&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=56934258&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=59475268&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=59500453&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=63948584&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=54463882&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=57363087&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=53401333&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=53362208&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=61535393&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=53772526&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=62042424&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=60793504&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=54205186&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=67555765&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=61870266&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=64359248&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=64712868&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=64343194&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=62020210&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=62150143&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=59604963&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=66003447&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=62471669&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=56920431&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=62570377&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=55946308&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=62897956&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=59487761&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=58105440&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=63947171&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=61401082&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=64784885&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=57603935&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=62471669&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=58956831&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=58434561&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=59604963&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=64219484&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=63968846&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=67555765&l=zh-Hans&t=1',
        # 'https://like.video/live/share/profile?c=cp&b=61710631&l=zh-Hans&t=1',
    ]

    def __init__(self, *a, **kw):
        super(LikeSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        url = self.channel_list.pop()
        yield Request(
            url,
            headers=self.hd,
            dont_filter=True,
            callback=self.parse_list
        )
        # for category in categories:
        #     url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % (category, 1)
        #     yield Request(url, meta={'tag': categories[category], 'category_name': category, 'index': 1},
        #                   callback=self.page)  # simulate login request

        # for category in categories:
        #     url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % (category, 1)
        #     yield Request(url, meta={'tag': categories[category], 'category_name': category, 'index': 1},
        #                   callback=self.page)  # simulate login request

        # url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % (category, 1)
        #     yield Request(url, meta={'tag': categories[category], 'category_name': category, 'index': 1},
        #                   callback=self.page)  # simulate login request

        # test_url = 'http://www.alarabiya.net/ar/medicine-and-health/2017/11/26/%D9%87%D9%84-%D9%8A%D8%AA%D8%B3%D8%A8%D8%A8-%D8%AA%D8%B1%D9%85%D8%A8-%D9%81%D9%8A-%D8%B2%D9%8A%D8%A7%D8%AF%D8%A9-%D8%A3%D8%B9%D8%AF%D8%A7%D8%AF-%D8%A7%D9%84%D9%85%D8%B5%D8%A7%D8%A8%D9%8A%D9%86-%D8%A8%D8%A7%D9%84%D9%85%D9%84%D8%A7%D8%B1%D9%8A%D8%A7%D8%9F.html'
        # yield Request(test_url, callback=self.article)  # simulate login request
        pass

    def parse_list(self, response):
        raw = {}
        raw['publisher'] = re.findall('"nick_name":"(.*?)"', response.body_as_unicode())[0]
        raw['uid'] = re.findall('"uid":"(.*?)"', response.body_as_unicode())[0]

        post_url = 'https://like.video/bg_ci_index.php/live/share/getUserPost?u=%s&count=%s' \
                   % (raw['uid'], self.max_request_video_count)
        post_list = requests.get(post_url).json()['post_list']
        for each in post_list:
            raw['source_url'] = each['share_url']
            yield Request(
                raw['source_url'],
                headers=self.hd,
                dont_filter=True,
                meta=raw,
                callback=self.parse_article
            )
            # print raw

    def parse_article(self, response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        # try:
        #     subtitle = soup.find('div', attrs={'id': 'microformat'}).get_text().replace(' - YouTube', '').strip()
        # except Exception, e:
        #     self.logger.warning(e)
        #     self.logger.warning('no subtitle!')
        #     return
        #     time.sleep(5)
        #     yield Request(
        #         response.url,
        #         headers=self.hd,
        #         dont_filter=True,
        #         callback=self.parse_list
        #     )
        #     return

        raw = response.meta
        raw['doc_id'] = str(response.url).split('/')[-1]
        # 生成唯一title
        raw['title'] = "%s(%s)" % (re.findall('<title>(.*?)</title>', response.body_as_unicode())[0], raw['doc_id'])
        raw['video'] = re.findall('(.*?)\?crc', soup.find('video', attrs={'id': 'videoPlayer'}).attrs['src'])[0]
        raw['image'] = soup.find('div', attrs={'class': 'video'}).find('div').find('img').get('src')
        raw['video_width'] = soup.find('video', attrs={'id': 'videoPlayer'}).attrs['width']
        raw['video_height'] = soup.find('video', attrs={'id': 'videoPlayer'}).attrs['height']
        raw['duration'] = 15

        # raw['image'] = re.findall('(.*?)\?wmk_sdk', soup.find('div', attrs={'class': 'host clearfix'}).div.div.img.attrs['src'])[0]
        # raw['video'] = re.findall('<video id="videoPlayer" class="video-js" src="(.*?)\?crc=', body)[0]
        # raw['video'] = re.findall('<video id="videoPlayer" class="video-js" src="(.*?)\?crc=', body)[0]
        # raw['image'] = re.findall('<video id="videoPlayer" class="video-js" src="(.*?)?crc=', response.body_as_unicode())[0]
        print raw

    # print(raw)
    # print response.body_as_unicode()
    # has_more = tjson['has_more']
    # max_cursor = tjson['max_cursor']
    # if has_more:
    #     url = 'https://www.douyin.com/aweme/v1/aweme/post/?user_id=%s&count=21&max_cursor=%d' % (
    #     self.uid, int(max_cursor))
    #     yield Request(
    #         url,
    #         headers=self.hd,
    #         dont_filter=True,
    #         callback=self.parse_list
    #     )

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
        if index > 2:
            return
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
        date_str = re.findall("(\d{4}/\d{1,2}/\d{1,2})", response.url)[0]
        raw['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(date_str, '%Y/%m/%d'))
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
        with open('bbc_message_extra.txt', 'a') as f:
            f.write(json.dumps(raw) + '\n')

        pass
