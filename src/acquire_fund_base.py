'''
Desc: 获取晨星单支基金的基础信息 -- 代码，名称，分类基金公司，成立时间等这些基金一成立都不会变动的信息
File: /acquire_fund_base.py
Project: src
File Created: Monday, 8th March 2021 5:31:50 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''
from threading import Lock

from utils.settings import is_cookie_login
from utils.login import login_morning_star
from utils.index import bootstrap_thread
from fund_info.crawler import FundSpider
from lib.mysnowflake import IdWorker
from sql_model.fund_query import FundQuery
from sql_model.fund_insert import FundInsert

def acquire_fund_base():
    lock = Lock()
    each_fund_query = FundQuery()
    each_fund_insert = FundInsert()

    record_total = each_fund_query.get_fund_count_from_snapshot_no_exist()    # 获取记录条数

    idWorker = IdWorker()
    print('record_total', record_total)
    error_funds = []  # 一些异常的基金详情页，如果发现记录该基金的code

    def crawlData(start, end):
        login_url = 'https://www.morningstar.cn/membership/signin.aspx'
        chrome_driver = login_morning_star(login_url, is_cookie_login)
        page_start = start
        page_limit = 10
        # 遍历从基金列表的单支基金
        while(page_start < end):
            results = each_fund_query.get_fund_from_snapshot_table_no_exist(
                page_start, page_limit)
            for record in results:
                each_fund = FundSpider(
                    record[0], record[1], record[2], chrome_driver)
                # 从晨星网上更新信息
                is_normal = each_fund.go_fund_url()
                if is_normal == False:
                    lock.acquire()
                    error_funds.append(each_fund.fund_code)
                    lock.release()
                    continue
                each_fund.get_fund_base_info()
                # 去掉没有成立时间的
                if each_fund.found_date == '-':
                    lock.acquire()
                    error_funds.append(each_fund.fund_code)
                    lock.release()
                    continue
                # 拼接sql需要的数据
                lock.acquire()
                snow_flake_id = idWorker.get_id()
                lock.release()
                base_dict = {
                    'id': snow_flake_id,
                    'fund_code': each_fund.fund_code,
                    'morning_star_code': each_fund.morning_star_code,
                    'fund_name': each_fund.fund_name,
                    'fund_cat': each_fund.fund_cat,
                    'company': each_fund.company,
                    'found_date': each_fund.found_date
                }
                each_fund_insert.insert_fund_base_info(base_dict)
            page_start = page_start + page_limit
            print('page_start', page_start)
        chrome_driver.close()
    
    bootstrap_thread(crawlData, record_total, 4)
    print('error_funds', error_funds)

if __name__ == '__main__':
    acquire_fund_base()
