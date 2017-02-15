# -*- coding:utf-8 -*-
import win32com
import oss2
import urllib
import requests
import ssl
import json
import sys
import time
import MySQLdb
import ConfigParser
from urllib import quote
import codecs
from selenium import webdriver
from lxml import etree
reload(sys)
sys.setdefaultencoding( "utf8" )
ssl._create_default_https_context = ssl._create_unverified_context

# 淘宝spider
# version:1.0
# language:python2.7
# date:2017-01-18
# author:ZeroDeng
# Email:denglin0105@vip.qq.com

print u'# 淘宝spider'
print u'# version:1.0'
print u'# language:python2.7'
print u'# date:2017-01-19'
print u'# author:ZeroDeng'
print u'# Email:denglin0105@vip.qq.com\n'

get_num = 1

#定义商品信息字段
name = ''#名字
act = ''#销量
location = ''#地区
fastPostFee = ''#运费
originalPrice = ''#原价
price = ''#折扣价
img2 = ''#预览照片url
url = ''#宝贝地址
userId = ''#店家id
######################

#获取配置信息
config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'), "rb")
dburl = str(config.get("mysqldb", "db_url"))
dbuser = str(config.get("mysqldb", "db_user"))
dbpassword = str(config.get("mysqldb", "db_password"))
dbname = str(config.get("mysqldb", "db_name"))
dbstatus = str(config.get("mysqldb", "db_status"))
runtime = str(config.get("RunTime", "run_time"))
OssStatus = str(config.get("OSS", "oss_status"))
Key = str(config.get("OSS", "Key"))
Secret = str(config.get("OSS", "Secret"))
BucketName = str(config.get("OSS", "BucketName"))
Endpoint = str(config.get("OSS", "Endpoint"))
Document = str(config.get("OSS", "Document"))

#######################
if runtime == '':
    print u'您没有配置系统运行间隔，系统将使用默认运行间隔为：24小时\n\n'
    runtime = 86400

def creatDB():# 创建数据表
    global dbstatus
    if dbstatus != '1':
        try:
            db = MySQLdb.connect(dburl, dbuser,dbpassword, dbname, charset='utf8')
            cur = db.cursor()
            # 执行sql语句
            cur.execute("CREATE TABLE  taobao (id int(11) NOT NULL AUTO_INCREMENT,`name` varchar(1000) DEFAULT NULL,`act` varchar(1000) DEFAULT NULL,`location` varchar(1000) DEFAULT NULL,`fastPostFee` varchar(1000) DEFAULT NULL,`originalPrice` varchar(1000) DEFAULT NULL,`price` varchar(1000) DEFAULT NULL,`img2` varchar(1000) DEFAULT NULL,`url` varchar(1000) DEFAULT NULL,`userId` varchar(1000) DEFAULT NULL,`keyword` varchar(1000) DEFAULT NULL,`datetime` datetime DEFAULT NULL,UNIQUE KEY `id` (`id`));")
            # 提交到数据库执行
            db.commit()
            print u'数据表创建完毕\n'
            config = ConfigParser.ConfigParser()
            config.readfp(open('config.ini'), "rb")
            config.set("mysqldb", "db_status", "1")
            config.write(open('config.ini', 'w'))
        except Exception,e:
            log = open('taobao_error.txt', 'a')
            print >> log, Exception, ":", e
            log.close()
            print u'创建数据表发生错误，请检查配置文件config.ini'
            print Exception, ":", e
            sys.exit()
        # 关闭数据库连接
        db.close()
def open_url(url_str):#打开url
    try:
        req = urllib.urlopen(url_str)
        date = req.read()
        json_py = json.loads(date)
    except:
        log = open('taobao_error.txt', 'a')
        print >> log, 'URL无效：' + str(url_str)  # 输出错误URL
        log.close()
        print Exception, ":", e
    return  json_py
def put_img(imgurl,num):#上传图片
    global OssStatus
    global Key
    global Secret
    global BucketName
    global Endpoint
    global Document

    if OssStatus=='1':
        auth = oss2.Auth(Key, Secret)
        endpoint =Endpoint
        bucket = oss2.Bucket(auth, endpoint, BucketName)
        try:
            input = requests.get('http:' + imgurl)
            bucket.put_object(Document + '%s.jpg' % str(num), input)
        except Exception, e:
            print Exception, ":", e
            log = open('taobao_error.txt', 'a')
            print >> log, Exception, ":", e
            log.close()
            print u'保存图片到oss发生错误'
    if OssStatus!='1':
        try:
            path = 'images/%s.jpg' % str(num)
            urllib.urlretrieve('http:' + imgurl, path)
        except Exception, e:
            print Exception, ":", e
            log = open('taobao_error.txt', 'a')
            print >> log, Exception, ":", e
            log.close()
            print u'保存图片到本地发生错误'
def start_py(keyword):#爬虫主进程，接受keword爬取的关键字
    global dburl
    global dbuser
    global dbpassword
    global dbname
    global get_num
    select_count = 0 #统计爬取次数
    if keyword != '':
        unkeyword = keyword
        keyword = quote(keyword)
    url_base = 'http://s.m.taobao.com/search?q=' + keyword + '&search=%E6%8F%90%E4%BA%A4&tab=all&sst=1&n=20&buying=buyitnow&m=api4h5&abtest=23&wlsort=23&page=1'
    if open_url(url_base)['RN'] != "":
        page_sum = open_url(url_base)['totalPage']  # 该关键词查询到的总页数
    else:
        page_sum = 1
    page = 1
    for page in range(int(page_sum)):
        url_taobao = 'http://s.m.taobao.com/search?q=' + keyword + '&search=%E6%8F%90%E4%BA%A4&tab=all&sst=1&n=20&buying=buyitnow&m=api4h5&abtest=23&wlsort=23&page=' + str(
            page+1)  # url模板
        try:
            listItem = open_url(url_taobao)['listItem']#当前页商品集合
        except:
            log = open('taobao_error.txt', 'a')
            print >> log,'错误URL：'+ str(url_taobao)#输出错误URL
            log.close()
            print Exception, ":", e
        good_num = len(listItem)#当前页商品数量
        i = 0  # 初始化循环变量i
        while i < good_num:
            datetime = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))  # 当前时间
            good_info = listItem[i]
            try:
                name = good_info['name']
            except:
                name = "null"
            try:
                location = good_info['location']
            except:
                location = "null"
            try:
                act = good_info['act']
            except:
                act = "null"
            try:
                fastPostFee = good_info['fastPostFee']
            except:
                fastPostFee = "null"
            try:
                originalPrice = good_info['originalPrice']
            except:
                originalPrice = "null"
            try:
                price = good_info['price']
            except:
                price = "null"
            try:
                img2 = good_info['img2']
            except:
                img2 = "null"
            try:
                url = good_info['url']
            except:
                url ="null"
            try:
                userId = good_info['userId']
            except:
                userId = "null"
            print u'系统正在获取第'+ str(get_num)+ u'条数据'
            photo_mum = get_num
            if name!= '':
                get_num += 1
                select_count += 1
                # 打开数据库连接
                db = MySQLdb.connect(dburl, dbuser,dbpassword, dbname, charset='utf8')
                cur = db.cursor()
                sql = "insert into taobao (name,act,location,fastPostFee,originalPrice,price,img2,url,userId,keyword,datetime) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"%(
                    str(name), str(act), str(location), str(fastPostFee), str(originalPrice), str(price), str(img2),
                    str(url), str(userId), str(unkeyword), str(datetime))
                try:
                    # 执行sql语句
                    cur.execute(sql)
                    # 提交到数据库执行
                    db.commit()
                except Exception,e:
                    # 发生错误时回滚
                    print Exception, ":", e
                    log = open('taobao_error.txt', 'a')
                    print >> log, Exception, ":", e
                    log.close()
                    print u'数据库连接错误，请检查配置文件config.ini'
                    sys.exit()
                    db.rollback()
                # 关闭数据库连接
                db.close()
                put_img(img2,photo_mum)
            i += 1
        page += 1
    return select_count #返回关键词宝贝数量
def hot_keyword():#获取淘宝热搜关键词
    try:
        url = 'https://top.taobao.com/index.php?spm=a1z5i.1.7.11.OXERXt&rank=focus&type=up'
        driver = webdriver.PhantomJS()
        driver.get(url)
        html = driver.page_source
        tree = etree.HTML(html)
    except Exception, e:
        log = open('taobao_error.txt', 'a')
        print >> log, Exception, ":", e
        log.close()
        print u'接口错误...'
        print Exception, ":", e
    num = 2
    keywords = {}
    while num <= 21:
        status = True
        try:
            keyword = tree.xpath('//*[@id="bang-wbang"]/div/div/div/ul/li['+ str(num) + ']/div/div[2]/div/a')[0].text
        except Exception, e:
            log = open('taobao_error.txt', 'a')
            print >> log, Exception, ":", e
            log.close()
            print u'获取关键词出错'
            print Exception, ":", e
            status = False
        keywords[num] = keyword
        print u'即将开始检索的关键词'+ str(num-1) + ':' + keywords[num]
        if status:
            num += 1
    return keywords
def start():#开始
    keyords = hot_keyword()
    num = 2
    while num <= 21:
        try:
            keyword = str(keyords[num])
            print u'【下面开始查询的关键词：' + keyword + u'】'
            start_py(keyword)
            num += 1
        except Exception, e:
            log = open('taobao_error.txt', 'a')
            print >> log, Exception, ":", e
            log.close()
            print u'关键词有误...'
            print Exception, ":", e


Runstatus = raw_input(unicode('是否开始（Y/N）：','utf-8').encode('gb2312'))
if Runstatus=='Y'or Runstatus=='y':
    while True:
        creatDB()
        print u'当前运行时间为：' + time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
        print u'下次运行时间为本次运行结束后' + str(int(runtime)/60) + u'分钟\n'
        time.sleep(int(1))
        print u'数据大礼包准备中，请勿关闭...\n'
        start()
        print u'\nThe End'
        print u'系统正在等待下次运行...'
        nowtime = time.time()
        print u'下次运行时间为：' + time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(nowtime + runtime))
        time.sleep(int(runtime))
if Runstatus=='N' or Runstatus=='n':
    print u'系统已经终止...'




