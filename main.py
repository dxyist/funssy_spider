#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Usage:
    main.py [--result=result]
"""
import os
# 这个参数用于生成命令行解释器


os.system("scrapy crawl alarabiya")
#os.system("scrapy crawl funssy")


# args = docopt(__doc__)
# # 默认参数
# if args['--result'] is None:
#     args['--result'] = "items.jl"
# # 配置文件位置
# args['--config'] = "_config.ini"
#
# # cmdline.execute("scrapy crawl github".split())
#
# os.system("rm -rf %s" % args["--result"])
# os.system("scrapy crawl github -o %s -a config_path=%s" % (args["--result"], args['--config']))
# os.system("python3 json_handler.py %s" % args["--config"])



