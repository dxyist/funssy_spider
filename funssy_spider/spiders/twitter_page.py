# -*- coding: utf-8 -*-
import scrapy
from scrapy import log
from scrapy.http import FormRequest
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import datetime
import json
import re
import hashlib

import lxml.html
import urllib2
from lxml import etree


class AlarabiyaSpider(scrapy.Spider):
    name = 'twitter_page'
    # allowed_domains = ['http://www.alarabiya.net']
    # start_urls = ['http://http://www.bbc.com/arabic/middleeast/']
    download_delay = 0

    def start_requests(self):
        url = 'https://twitter.com/Tim_Duffy'
        yield Request(url, callback=self.userinfo)  # simulate login request
        pass

    def userinfo(self, response):
        body_instance = response.body
        start_ts = datetime.datetime.now()

        parse_user_info(body_instance)
        tree = lxml.html.fromstring(body_instance)
        raw = {}
        results = {}
        # xpathselector = "/body/div/div[2]/div/div[5]/div[2]/div/ol/li[5]/div/div/p"
        # xpathselector = "/body/div/div[2]/div/div[5]/div[2]/div/ol/li[5]/div/div/p"
        name_selector = '//*[@id="page-container"]/div[2]/div/div/div[1]/div/div/div/div[@class="ProfileHeaderCard"]/h1[@class="ProfileHeaderCard-name"]/a/text()'
        location_selector = '//*[@id="page-container"]/div[2]/div/div/div[1]/div/div/div/div[@class="ProfileHeaderCard"]/div[@class="ProfileHeaderCard-location "]/span[@class="ProfileHeaderCard-locationText u-dir"]/a/text()'
        join_date_selector = '//*[@id="page-container"]/div[2]/div/div/div[1]/div/div/div/div[@class="ProfileHeaderCard"]/div[@class="ProfileHeaderCard-joinDate"]/span[@class="ProfileHeaderCard-joinDateText js-tooltip u-dir"]/@title'
        tweets_selector = '//*[@id="page-container"]/div[1]/div/div[2]/div/div/div[2]/div/div/ul/li[@class="ProfileNav-item ProfileNav-item--tweets is-active"]/a/span[3]/@data-count'
        following_selector = '//*[@id="page-container"]/div[1]/div/div[2]/div/div/div[2]/div/div/ul/li[@class="ProfileNav-item ProfileNav-item--following"]/a/span[3]/@data-count'
        followers_selector = '//*[@id="page-container"]/div[1]/div/div[2]/div/div/div[2]/div/div/ul/li[@class="ProfileNav-item ProfileNav-item--followers"]/a/span[3]/@data-count'
        likes_selector = '//*[@id="page-container"]/div[1]/div/div[2]/div/div/div[2]/div/div/ul/li[@class="ProfileNav-item ProfileNav-item--favorites"]/a/span[3]/@data-count'
        photos_and_videos_selector = '//*[@id="page-container"]/div[2]/div/div/div[1]/div/div/div/div[2]/div[1]/span[2]/a[1]/text()'

        # home_page_selector = '//*[@id="page-container"]/div[2]/div/div/div[1]/div/div/div/div[1]/div[2]/span[2]/a'
        tweet_time_selector = '//*[@data-item-type="tweet"]/div/div[2]/div[@class="stream-item-header"]/small[@class="time"]/a/span/@data-time'
        tweet_comment_number_selector = '//*[@data-item-type="tweet"]/div/div[2]/div[4]/div[@class="ProfileTweet-actionList js-actions"]/div[@class="ProfileTweet-action ProfileTweet-action--reply"]/button/span/span/text()'
        tweet_retweet_number_selector = '//*[@data-item-type="tweet"]/div/div[2]/div[4]/div[@class="ProfileTweet-actionList js-actions"]/div[@class="ProfileTweet-action ProfileTweet-action--retweet js-toggleState js-toggleRt"]/button[@class="ProfileTweet-actionButton  js-actionButton js-actionRetweet"]/span/span/text()'
        tweet_favorite_number_selector = '//*[@data-item-type="tweet"]/div/div[2]/div[4]/div[@class="ProfileTweet-actionList js-actions"]/div[@class="ProfileTweet-action ProfileTweet-action--favorite js-toggleState"]/button[@class="ProfileTweet-actionButton js-actionButton js-actionFavorite"]/span/span/text()'

        protected_selector = '//*[@id="page-container"]/div[2]/div/div/div[2]/div/div[1]/div/div[@class="ProtectedTimeline"]/@class'
        has_not_tweeted_selector = '//*[@id="page-container"]/div[2]/div/div/div[2]/div/div[2]/div[@class="ProfilePage-emptyModule"]/h3/text()'

        raw['name'] = tree.xpath(name_selector)
        raw['source_url'] = response.url
        raw['join_date'] = tree.xpath(join_date_selector)
        raw['tweets'] = tree.xpath(tweets_selector)
        raw['following'] = tree.xpath(following_selector)

        raw['followers'] = tree.xpath(followers_selector)
        raw['likes'] = tree.xpath(likes_selector)
        raw['location'] = tree.xpath(location_selector)
        raw['photos_and_videos'] = tree.xpath(photos_and_videos_selector)
        # raw['home_page'] = tree.xpath(home_page_selector)[0].text.strip()
        raw['tweet_times'] = tree.xpath(tweet_time_selector)
        raw['is_protected'] = tree.xpath(protected_selector)
        raw['has_not_tweeted'] = tree.xpath(has_not_tweeted_selector)
        raw['tweet_comment_numbers'] = tree.xpath(tweet_comment_number_selector)
        raw['tweet_retweet_numbers'] = tree.xpath(tweet_retweet_number_selector)
        raw['tweet_favorite_numbers'] = tree.xpath(tweet_favorite_number_selector)
        print raw

        pass

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
        with open('bbc_message_extra.txt', 'a') as f:
            f.write(json.dumps(raw) + '\n')

        pass


def parse_user_info(html):
    soup = BeautifulSoup(html, 'lxml')
    return dict(screenname=parse_screenname(soup),
                realname=parse_realname(soup),
                followers=parse_followers(soup),
                following=parse_following(soup),
                description=parse_description(soup),
                location=parse_location(soup),
                create_time=parse_create_time(soup), )

    screenname = parse_screenname(soup)
    realname = parse_realname(soup)
    followers = parse_followers(soup)
    following = parse_following(soup)
    description = parse_description(soup)
    location = parse_location(soup)
    create_time = parse_create_time(soup)
    # return following, followers, description, location, create_time


def parse_screenname(soup):
    tnode = soup.find('b', attrs={'class': 'u-linkComplex-target'})
    if not tnode:
        return None
    return tnode.get_text().strip()


def parse_realname(soup):
    tnode = soup.find('a', attrs={'class': 'ProfileHeaderCard-nameLink'})
    if not tnode:
        return None
    return tnode.get_text().strip()


def parse_following(soup):
    tnode = soup.find('li', attrs={'class': 'ProfileNav-item--following'})
    if not tnode:
        return None
    tnode = tnode.find('span', attrs={'class': 'ProfileNav-value'})
    if not tnode:
        return None
    return tnode.attrs['data-count']


def parse_followers(soup):
    tnode = soup.find('li', attrs={'class': 'ProfileNav-item--followers'})
    if not tnode:
        return None
    tnode = tnode.find('span', attrs={'class': 'ProfileNav-value'})
    if not tnode:
        return None
    return tnode.attrs['data-count']


def parse_description(soup):
    tnode = soup.find('p', attrs={'class': 'ProfileHeaderCard-bio'})
    if not tnode:
        return None
    return tnode.get_text().strip()


def parse_location(soup):
    tnode = soup.find('span', attrs={'class': 'ProfileHeaderCard-locationText'})
    if not tnode:
        return None
    return tnode.get_text().strip()


def parse_create_time(soup):
    tnode = soup.find('span', attrs={'class': 'ProfileHeaderCard-joinDateText'})
    if not tnode:
        return None
    return tnode.attrs['title'] if 'title' in tnode.attrs else ''


def parse_user_friends(html):
    soup = BeautifulSoup(html, 'lxml')
    ans = []
    for sp in soup.find_all('div', attrs={'class': 'js-actionable-user'}):
        ans.append(sp.attrs['data-screen-name'])
    return ans


def parse_friends(soup):
    return
