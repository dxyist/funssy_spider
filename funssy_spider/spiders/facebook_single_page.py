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
from ..feeds_back_utils import *


class FacebookSpider(scrapy.Spider):
    name = 'facebook_single'
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
        'https://www.facebook.com/findmeafunnyvideo/videos/2097671723591126/',
        # 'https://www.facebook.com/findmeafunnyvideo/videos/2097606853597613/',
        # 'https://www.facebook.com/findmeafunnyvideo/videos/1990760991244729/',
    ]

    def __init__(self, *a, **kw):
        super(FacebookSpider, self).__init__(*a, **kw)
        self.channel_list = get_channel_list('facebook_tops', 'United States of America')
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
            callback=self.parse_single_page
        )

    def parse_single_page(self, response):
        body_instance = response.body_as_unicode()
        tree = lxml.html.fromstring(body_instance)
        raw = {}
        publisher_selector = '//*[@id="facebook"]/head/meta[4]/@content'
        title_selector = '//*[@id="facebook"]/head/meta[5]/@content'
        thumbnails_selector = '//*[@id="facebook"]/head/meta[6]/@content'
        video_selector = '//*[@id="facebook"]/body/script[9]/text()'

        # with open('C:\Users\Leon\PycharmProjects\\funssy_spider\\body_instance','a') as f:
        #     f.write(str(response.head))
        video_data = re.findall('videoData:\[(.*?)\}', tree.xpath(video_selector)[0].strip())[0] + '}'

        # #raw['video_data'] = video_data
        raw['video'] = re.findall('sd_src:\"(.*?)\",', video_data)[0]
        raw_duration = re.findall('\d+', re.findall('Duration: (.*?) second', body_instance)[0])
        raw_duration = map(int, raw_duration)
        raw_duration.reverse()


        # for each in raw_duration:

        print(raw_duration)
        # raw['duration'] = (
        #     int(raw_duration.split('minute,')[-2].strip()) * 60 + int(raw_duration.split('minute,')[-1].strip()) if len(
        #         raw_duration.split('minute,')) == 2 else int(raw_duration.split('minute,')[-1].strip()))


        # # raw['duration'] = int()
        # raw['title'] = tree.xpath(title_selector)[0].strip()
        # # raw['subtitle'] = tree.xpath(publisher_selector)[0]
        # raw['publisher'] = tree.xpath(publisher_selector)[0]
        # raw['source_url'] = response.url
        # raw['thumbnails'] = [tree.xpath(thumbnails_selector)[0]]
        # # raw['time'] = tree.xpath(published_date_selector)[0]
        # raw['doc_id'] = re.findall('videos/([0-9]+)', response.url)[0]
        # raw['video_width'] = re.findall('original_width:(.*?),', video_data)[0]
        # raw['video_height'] = re.findall('original_height:(.*?),', video_data)[0]
        # # raw['genre'] = tree.xpath(genre_selector)[0]
        # # raw['hit_counts'] = tree.xpath(hitcount_selector)[0]



        print(raw)

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
