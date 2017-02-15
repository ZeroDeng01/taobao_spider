# taobao_spider
淘宝热搜词分析爬虫项目


基于python2.7开发，其中使用了phantomjs插件。
config.ini为基本配置文件，说明如下：
```
[mysqldb]
db_url = 127.0.0.1          数据库连接地址，默认3306端口
db_user = root              数据库用户名
db_password = 520love..@    数据库密码
db_name = python            数据库名
db_status = 1               是否在该数据库创建数据表taobao，未创建为0,已创建为1

[RunTime]                   
run_time = 86401            爬虫运行时间间隔，单位秒

[OSS]
oss_status = 0                                     是否使用阿里云oss存储照片附件，是为1否为0
Key = LJ53LvR1Q1118Qhi                             阿里云key
Secret = xikfDIv67a3ZzclShnqUPRo11qEJtK            阿里云Secret
BucketName = python1223                            oss BucketName
Endpoint = http://oss-cn-beijing.aliyuncs.com      oss地址
Document = images/                                 文件存放路径
```

