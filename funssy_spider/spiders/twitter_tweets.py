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
    name = 'twitter_tweets'
    # allowed_domains = ['http://www.alarabiya.net']
    # start_urls = ['http://http://www.bbc.com/arabic/middleeast/']
    download_delay = 0

    def start_requests(self):
        url = 'https://twitter.com/joselinarespsuv'
        yield Request(url, callback=self.user_content)  # simulate login request
        pass

    def user_content(self, response):
        body_instance = response.body
        tree = lxml.html.fromstring(body_instance)
        raw = {}

        tweets_container = []
        tweets_contents = tree.xpath('//li[starts-with(@class,"js-stream-item stream-item stream-item")]')
        # print etree.tostring(tweets_contents[0].xpath('div[1]/div[2]/div[3]/div[2]/div[1]/button')[0], method='html')
        index = 0;
        for item in tweets_contents:
            # if (index == 1):
            #     print etree.tostring(item.xpath('div[1]')[0], method='html')
            print(index)
            tweets = {}
            re_ptn = re.compile('pic.twitter.com/\S+')

            try:
                tweets["content"] = re_ptn.sub('',
                                               item.xpath(
                                                   'div[1]/div[@class="content"]/div[@class="js-tweet-text-container"]/p')[
                                                   0].xpath(
                                                   'string(.)').replace(u'\xa0', ' '))
            except:
                continue
            print(tweets["content"])
            '//*[@id="stream-item-tweet-873264379910909952"]/div[1]/div[2]/div[2]/p'
            tweets["ts"] = item.xpath(
                'div/div[2]/div[@class="stream-item-header"]/small[@class="time"]/a/span/@data-time')

            tweets["id"] = item.xpath(
                '@data-item-id')
            tweets["comments"] = item.xpath(
                'div/div[2]/div[@class="stream-item-footer"]/div[1]/span[@class="ProfileTweet-action--reply u-hiddenVisually"]/span/@data-tweet-stat-count')
            tweets["retweets"] = item.xpath(
                'div/div[2]/div[@class="stream-item-footer"]/div[1]/span[@class="ProfileTweet-action--retweet u-hiddenVisually"]/span/@data-tweet-stat-count')
            tweets["favorites"] = item.xpath(
                'div/div[2]/div[@class="stream-item-footer"]/div[1]/span[@class="ProfileTweet-action--favorite u-hiddenVisually"]/span/@data-tweet-stat-count')

            tweets_container.append(tweets)
            index += 1
            # comment_url = response.url + "/status/" + str(tweets['id'][0])
            # yield Request(comment_url, callback=self.user_comments)
        # raw['uid'] = response.meta['uid']
        raw['content'] = tweets_container
        # raw['_id'] = raw['uid']
        raw['insert_time'] = time.time()

        print(json.dumps(raw))

    def user_comments(self, response):
        body_instance = response.body
        tree = lxml.html.fromstring(body_instance)
        comment_container = []

        comment_sections = tree.xpath('//li[@class="ThreadedConversation"]')
        for section in comment_sections:
            comment_session = []
            comments_paths = section.xpath('ol/div[@class="ThreadedConversation-tweet"]')
            for item in comments_paths:
                comment = {}

                comment['user'] = item.xpath(
                    'li/div/div/div[@class="stream-item-header"]/a/span[@class="FullNameGroup"]/strong/text()')
                comment['ts'] = item.xpath(
                    'li/div/div/div[@class="stream-item-header"]/small/a/span/@data-time')
                comment['content'] = item.xpath(
                    'li/div/div/div[@class="js-tweet-text-container"]')[0].xpath(
                    'string(.)').replace(u'\xa0', ' ')
                comment_session.append(comment)
            comment_container.append(comment_session)
        # Other type of comments
        comment_sections = tree.xpath('//li[contains(@class,"ThreadedConversation--")]')
        for section in comment_sections:
            comment_session = []
            comments_paths = section.xpath('ol')

            for item in comments_paths:
                comment = {}
                comment['user'] = item.xpath(
                    'li/div/div/div[@class="stream-item-header"]/a/span[@class="FullNameGroup"]/strong/text()')
                comment['ts'] = item.xpath(
                    'li/div/div/div[@class="stream-item-header"]/small/a/span/@data-time')
                comment['content'] = item.xpath(
                    'li/div/div/div[@class="js-tweet-text-container"]')[0].xpath(
                    'string(.)').replace(u'\xa0', ' ')
                comment_session.append(comment)
            comment_container.append(comment_session)

            # print(len(comment_container))
            # print(comment_container)

    def userinfo(self, response):
        body_instance = response.body
        start_ts = datetime.datetime.now()

        parse_user_info(body_instance)
        tree = lxml.html.fromstring(body_instance)
        raw = {}
        results = {}
        tweets_container = []
        tweets_contents = tree.xpath('//li[@data-item-type="tweet"]')
        print(len(tweets_contents))
        # print(tweets_contents[0].xpath('div/div[@class="content"]/div[@class="js-tweet-text-container"]/p')[0].xpath(
        #                                        'string(.)'))
        # print etree.tostring(tweets_contents[0].xpath('div/div[@class="content"]/div[@class="js-tweet-text-container"]/p')[0], method='html')
        for item in tweets_contents:
            tweets = {}
            re_ptn = re.compile('pic.twitter.com/\S+')

            try:
                tweets['content'] = re_ptn.sub('',
                                               item.xpath(
                                                   'div[@class="content"]/div[@class="js-tweet-text-container"]/p')[
                                                   0].xpath(
                                                   'string(.)'))
            except:
                print('error!!!!!!!!!!!!!!!!!!!!!!!!!!')
                try:
                    print etree.tostring(
                        item.xpath('div/div[@class="content"]')[0],
                        method='html')
                except:
                    print('double error!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    print etree.tostring(
                        item.xpath('div')[0],
                        method='html')

            tweets['ts'] = item.xpath(
                'div/div[2]/div[@class="stream-item-header"]/small[@class="time"]/a/span/@data-time')
            tweets['id'] = item.xpath(
                'div/div[2]/div[@class="stream-item-header"]/small[@class="time"]/a/span/@data-time')
            tweets['comments'] = item.xpath(
                'div/div[2]/div[@class="stream-item-footer"]/div[1]/span[@class="ProfileTweet-action--reply u-hiddenVisually"]/span/@data-tweet-stat-count')
            tweets['retweets'] = item.xpath(
                'div/div[2]/div[@class="stream-item-footer"]/div[1]/span[@class="ProfileTweet-action--retweet u-hiddenVisually"]/span/@data-tweet-stat-count')
            tweets['favorites'] = item.xpath(
                'div/div[2]/div[@class="stream-item-footer"]/div[1]/span[@class="ProfileTweet-action--favorite u-hiddenVisually"]/span/@data-tweet-stat-count')

            tweets_container.append(tweets)

        # raw['tweets'] = tree.xpath(tweets_selector)
        # raw['source_url'] = response.url
        import pprint
        pprint.pprint(tweets_container)

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
