# -*- coding:utf-8 -*-

# 爬取港交所数据

import sys

from hkex import *
from crawler import *

sys.path.append("../../lib/log")
from log import *

def usage():
    ''' 展示帮助信息 '''
    print("python3 ./main.py [stock|transaction]")
    print("     - stock: 爬取股票数据")
    print("     - transaction: 爬取交易数据")
    print("     - help: 展示帮助信息")


if __name__ == "__main__":
    # 校验参数
    if len(sys.argv) < 2:
        usage() 
        exit(-1)

    # 日志初始化
    log_init("../../../log/crawler.log")

    # 新建爬虫对象
    crawler = Crawler()

    func = sys.argv[1]
    if func == "stock":
        # 爬取股票信息
        crawler.crawl_stock()
    elif func == "transaction":
        # 爬取交易信息
        stock_code = sys.argv[2]
        crawler.crawl_transaction(stock_code)
    else:
        usage()

