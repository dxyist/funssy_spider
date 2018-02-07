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
import cv2.cv as cv
import lxml
from urllib import unquote

class YoutubeSpider(scrapy.Spider):
    name = 'youtube_single'
    # allowed_domains = ['http://www.alarabiya.net']
    # start_urls = ['http://http://www.bbc.com/arabic/middleeast/']
    download_delay = 0
    hd = {'pragma': 'no-cache',
          'cache-control': 'no-cache'}
    page = 0
    max_page = 30
    max_duration = 300
    # channel_list = get_channel_list('like', 'Thailand')
    channel_list = [
        # 'https://www.youtube.com/watch?v=YmLwu1hQLIc',
        # 'https://www.youtube.com/watch?v=usosU1XnEow',
        # 'https://www.youtube.com/watch?v=NLGLl_fSIMI',
        'https://www.youtube.com/watch?v=TqKOni-Qyuw',
        'https://www.youtube.com/watch?v=JHD2f38MlDk',
        'https://www.youtube.com/watch?v=hUADnAxNf6U',
        'https://www.youtube.com/watch?v=VSKuhdmYkUU',
        'https://www.youtube.com/watch?v=3tUCuMSPQwE',
        'https://www.youtube.com/watch?v=uUukt4SGeT0',
        'https://www.youtube.com/watch?v=-SY-aeSplco',
        'https://www.youtube.com/watch?v=4BiWtH0HywY',
        'https://www.youtube.com/watch?v=No35-c4zXjo',
        'https://www.youtube.com/watch?v=MVkkdjUoHI4',
    ]

    def __init__(self, *a, **kw):
        super(YoutubeSpider, self).__init__(*a, **kw)
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
            callback=self.parse_page
        )


    def parse_page(self, response):
        # print response.url

        body_instance = response.body_as_unicode()
        tree = lxml.html.fromstring(body_instance)
        raw = {}
        # title_selector = '//*[@id="page-container"]/div[2]/div/div/div[1]/div/div/div/div[@class="ProfileHeaderCard"]/h1[@class="ProfileHeaderCard-name"]/a/text()'
        # title_selector = '//*[@id="watch-header"]/div[@id="watch7-headline"]/div[@id="watch-headline-title"]/h1[@class="watch-title-container"]/span/text()'
        subtitle_selector = '//*[@id="watch-header"]/div[@id="watch7-user-header"]/div/a/text()'
        thumbnails_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/span[@itemprop="thumbnail"]/link/@href'
        duration_raw_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="duration"]/@content'
        video_id_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="videoId"]/@content'
        title_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="name"]/@content'
        published_date_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="datePublished"]/@content'
        hitcount_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="interactionCount"]/@content'
        width_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="width"]/@content'
        height_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="height"]/@content'
        genre_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="genre"]/@content'

        raw['title'] = tree.xpath(title_selector)[0].strip()
        raw['subtitle'] = tree.xpath(subtitle_selector)[0]
        raw['publisher'] = tree.xpath(subtitle_selector)[0]
        raw['source_url'] = response.url
        raw['thumbnails'] = [tree.xpath(thumbnails_selector)[0]]
        raw['time'] = tree.xpath(published_date_selector)[0]
        raw['doc_id'] = tree.xpath(video_id_selector)[0]
        raw['video_width'] = tree.xpath(width_selector)[0]
        raw['video_height'] = tree.xpath(height_selector)[0]
        raw['genre'] = tree.xpath(genre_selector)[0]
        raw['hit_counts'] = tree.xpath(hitcount_selector)[0]

        # 正则获取播放时间
        m_value, s_value = \
        re.findall('PT([0-9]+)M([0-9]+)S', tree.xpath(duration_raw_selector)[0])[0]
        # second_value = re.findall('<meta itemprop="duration" content="PT[0-9]+M([0-9]+)S">', body_instance)[0]
        raw['duration'] = int(m_value) * 60 + int(s_value)
        # if raw['duration'] > self.max_duration:
        #     print('duration > %d' % self.max_duration)
        #     return
        yield Request(
            raw['source_url'],
            headers=self.hd,
            meta=raw,
            dont_filter=True,
            callback=self.parse_video
        )


    def parse_video(self, response):
        def _parse_stream_map(text):
            videoinfo = {
                "itag": [],
                "url": [],
                "quality": [],
                "fallback_host": [],
                "s": [],
                "type": []
            }
            videos = text.split(",")
            videos = [video.split("&") for video in videos]
            for video in videos:
                for kv in video:
                    key, value = kv.split("=")
                    videoinfo.get(key, []).append(unquote(value))
            return videoinfo

        ENCODING = {
            # Flash Video
            5: ["flv", "240p", "Sorenson H.263", "N/A", "0.25", "MP3", "64"],
            6: ["flv", "270p", "Sorenson H.263", "N/A", "0.8", "MP3", "64"],
            34: ["flv", "360p", "H.264", "Main", "0.5", "AAC", "128"],
            35: ["flv", "480p", "H.264", "Main", "0.8-1", "AAC", "128"],

            # 3GP
            36: ["3gp", "240p", "MPEG-4 Visual", "Simple", "0.17", "AAC", "38"],
            13: ["3gp", "N/A", "MPEG-4 Visual", "N/A", "0.5", "AAC", "N/A"],
            17: ["3gp", "144p", "MPEG-4 Visual", "Simple", "0.05", "AAC", "24"],

            # MPEG-4
            18: ["mp4", "360p", "H.264", "Baseline", "0.5", "AAC", "96"],
            22: ["mp4", "720p", "H.264", "High", "2-2.9", "AAC", "192"],
            37: ["mp4", "1080p", "H.264", "High", "3-4.3", "AAC", "192"],
            38: ["mp4", "3072p", "H.264", "High", "3.5-5", "AAC", "192"],
            82: ["mp4", "360p", "H.264", "3D", "0.5", "AAC", "96"],
            83: ["mp4", "240p", "H.264", "3D", "0.5", "AAC", "96"],
            84: ["mp4", "720p", "H.264", "3D", "2-2.9", "AAC", "152"],
            85: ["mp4", "1080p", "H.264", "3D", "2-2.9", "AAC", "152"],

            # WebM
            43: ["webm", "360p", "VP8", "N/A", "0.5", "Vorbis", "128"],
            44: ["webm", "480p", "VP8", "N/A", "1", "Vorbis", "128"],
            45: ["webm", "720p", "VP8", "N/A", "2", "Vorbis", "192"],
            46: ["webm", "1080p", "VP8", "N/A", "N/A", "Vorbis", "192"],
            100: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "128"],
            101: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "192"],
            102: ["webm", "720p", "VP8", "3D", "N/A", "Vorbis", "192"]
        }

        ENCODING_KEYS = (
            'extension',
            'resolution',
            'video_codec',
            'profile',
            'video_bitrate',
            'audio_codec',
            'audio_bitrate'
        )

        def _extract_fmt(text):
            itag = re.findall('itag=(\d+)', text)
            if itag and len(itag) is 1:
                itag = int(itag[0])
                attr = ENCODING.get(itag, None)
                if not attr:
                    return itag, None
                return itag, dict(zip(ENCODING_KEYS, attr))

        content = response.body_as_unicode()
        try:
            player_conf = content[18 + content.find("ytplayer.config = "):]
            bracket_count = 0
            i = 0
            for i, char in enumerate(player_conf):
                if char == "{":
                    bracket_count += 1
                elif char == "}":
                    bracket_count -= 1
                    if bracket_count == 0:
                        break
            else:
                self.logger.warning("Cannot get JSON from HTML")

            index = i + 1
            data = json.loads(player_conf[:index])
            # self.logger.warning(data)
        except Exception, e:
            self.logger.warning(e)
            return

        stream_map = _parse_stream_map(data["args"]["url_encoded_fmt_stream_map"])
        video_urls = stream_map["url"]
        raw = dict()
        raw.update(response.meta)
        for i, url in enumerate(video_urls):
            try:
                fmt, fmt_data = _extract_fmt(url)
                if fmt_data["extension"] == "mp4" and fmt_data["profile"] == "Baseline":
                    raw['video'] = url
                    self.logger.warning(url)
                    break
            except KeyError:
                continue
        # self.logger.warning(raw)

        # for request in self.parse_raw(raw):
        #     yield request

        print raw




        #
        # def parse_list(self, response):
        #     raw = {}
        #     raw['publisher'] = re.findall('"nick_name":"(.*?)"', response.body_as_unicode())[0]
        #     raw['uid'] = re.findall('"uid":"(.*?)"', response.body_as_unicode())[0]
        #
        #     post_url = 'https://like.video/bg_ci_index.php/live/share/getUserPost?u=%s&count=%s' \
        #                % (raw['uid'], self.max_request_video_count)
        #     post_list = requests.get(post_url).json()['post_list']
        #     for each in post_list:
        #         raw['source_url'] = each['share_url']
        #         yield Request(
        #             raw['source_url'],
        #             headers=self.hd,
        #             dont_filter=True,
        #             meta=raw,
        #             callback=self.parse_article
        #         )
        #         # print raw
        #
        # def parse_article(self, response):
        #     soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        #     # try:
        #     #     subtitle = soup.find('div', attrs={'id': 'microformat'}).get_text().replace(' - YouTube', '').strip()
        #     # except Exception, e:
        #     #     self.logger.warning(e)
        #     #     self.logger.warning('no subtitle!')
        #     #     return
        #     #     time.sleep(5)
        #     #     yield Request(
        #     #         response.url,
        #     #         headers=self.hd,
        #     #         dont_filter=True,
        #     #         callback=self.parse_list
        #     #     )
        #     #     return
        #
        #     raw = response.meta
        #     raw['doc_id'] = str(response.url).split('/')[-1]
        #     # 生成唯一title
        #     raw['title'] = "%s(%s)" % (re.findall('<title>(.*?)</title>', response.body_as_unicode())[0], raw['doc_id'])
        #     raw['video'] = re.findall('(.*?)\?crc', soup.find('video', attrs={'id': 'videoPlayer'}).attrs['src'])[0]
        #     raw['image'] = soup.find('div', attrs={'class': 'video'}).find('div').find('img').get('src')
        #     raw['video_width'] = soup.find('video', attrs={'id': 'videoPlayer'}).attrs['width']
        #     raw['video_height'] = soup.find('video', attrs={'id': 'videoPlayer'}).attrs['height']
        #     raw['duration'] = 15
        #
        #     # raw['image'] = re.findall('(.*?)\?wmk_sdk', soup.find('div', attrs={'class': 'host clearfix'}).div.div.img.attrs['src'])[0]
        #     # raw['video'] = re.findall('<video id="videoPlayer" class="video-js" src="(.*?)\?crc=', body)[0]
        #     # raw['video'] = re.findall('<video id="videoPlayer" class="video-js" src="(.*?)\?crc=', body)[0]
        #     # raw['image'] = re.findall('<video id="videoPlayer" class="video-js" src="(.*?)?crc=', response.body_as_unicode())[0]
        #     print raw
        #
        # # print(raw)
        # # print response.body_as_unicode()
        # # has_more = tjson['has_more']
        # # max_cursor = tjson['max_cursor']
        # # if has_more:
        # #     url = 'https://www.douyin.com/aweme/v1/aweme/post/?user_id=%s&count=21&max_cursor=%d' % (
        # #     self.uid, int(max_cursor))
        # #     yield Request(
        # #         url,
        # #         headers=self.hd,
        # #         dont_filter=True,
        # #         callback=self.parse_list
        # #     )
        #
        # def page(self, response):
        #     bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        #     items = bs.find_all("div", class_="item")
        #     if len(items) == 0:
        #         print("item == empty")
        #         return
        #     for item in items:
        #         title = item.find('a', class_='highline').text
        #         # subtitle = item.find('p', class_='eagle-item__summary').text
        #         create_time = item.find('div', class_='date').text
        #         page_url = self.base_url + item.find('a')['href']
        #         doc_id = (hashlib.md5(page_url.encode("utf8")).hexdigest())
        #         tag = response.meta['tag']
        #         meta = {'doc_id': doc_id,
        #                 'title': title,
        #                 'tag': tag,
        #                 # 'subtitle': subtitle,
        #                 'page_url': page_url,
        #                 'create_time': create_time}
        #         yield Request(page_url, meta=meta, callback=self.article)  # simulate login request
        #
        #     category_name = response.meta['category_name']
        #     index = response.meta['index']
        #     print("index:", index)
        #     if index > 2:
        #         return
        #     url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % (category_name, index + 1)
        #     yield Request(url, meta={'category_name': category_name, 'tag': tag, 'index': index + 1},
        #                   callback=self.page)  # simulate login request
        #
        # def article(self, response):
        #     raw = {}
        #     bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        #     #
        #     content_field = bs.find("article", class_="multi_articles")
        #     if content_field is None or len(content_field.find_all('video')) != 0:
        #         print(u"发现player视频页面!!!!!!")
        #         print(response.url)
        #         print('')
        #         return
        #
        #     if len(content_field.find_all("div", class_="article-default-image is-video")) != 0:
        #         print(u"发现youtube视频页面!!!!!!")
        #         print(response.url)
        #         print('')
        #         return
        #
        #     raw['title'] = response.meta['title']
        #     # raw['html'] = response.body
        #     raw['source_url'] = response.url
        #     raw['subtitle'] = 'alarabiya'
        #     raw['raw_tags'] = [response.meta['tag']]
        #     raw['doc_id'] = response.meta['doc_id']
        #     date_str = re.findall("(\d{4}/\d{1,2}/\d{1,2})", response.url)[0]
        #     raw['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(date_str, '%Y/%m/%d'))
        #     raw['content'] = []
        #
        #     # 先存第一张图
        #     title_img = content_field.find('div', class_='article_img')
        #     image = title_img.find('img')
        #     if image:
        #         image_content = {'text': '', 'image': image['src']};
        #         if image_content not in raw['content']:
        #             raw['content'].append(image_content)
        #             # print({'text': '', 'image': image['src']})
        #
        #     content_ps = content_field.find('div', class_='article-body').find_all({'p', 'figure'})
        #     for p in content_ps:
        #         image = p.find('img')
        #         if image:
        #             image_content = {'text': '', 'image': image['src']};
        #             if image_content not in raw['content']:
        #                 raw['content'].append(image_content)
        #                 # print({'text': '', 'image': image['src']})
        #
        #         else:
        #             raw['content'].append(
        #                 {'text': p.text.replace(u'\xa0', '').replace(u'\u3000', '').replace(u'\u200e', '')})
        #             # print({'text': p.text.replace('\xa0', '').replace('\u3000', '').replace('\u200e', '')})
        #
        #     print(raw['title'])
        #     # print(raw['source_url'])
        #     print(raw['subtitle'])
        #     print(raw['raw_tags'])
        #     print(raw['doc_id'])
        #     print(raw['time'])
        #     print(raw['content'])
        #     with open('bbc_message_extra.txt', 'a') as f:
        #         f.write(json.dumps(raw) + '\n')
        #
        #     pass
