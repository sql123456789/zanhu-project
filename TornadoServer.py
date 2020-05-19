# -*- coding: utf-8 -*-
__author__ = 'sql'
# date = 2020/5/16

import os
import sys
from pathlib import Path
from tornado.options import options, define
from django.core.wsgi import get_wsgi_application
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

# 将应用application加入到查找路径中
app_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
sys.path.append(os.path.join(app_path, 'zanhu'))  # ../zanhu/zanhu

# 配置tornado的端口
define("port", default = 6000, type=int, help = "run on the given port")

def main():
    tornado.options.parse_command_line()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
    # 放入wsgi服务
    wsgi_app = tornado.wsgi.WSGIContainer(get_wsgi_application())
    # 配置httpserver有了xheaders = True才能接收客户端的IP
    http_server = tornado.httpserver.HTTPServer(wsgi_app, xheaders = True)
    # 监听实例
    http_server.listen(options.port)
    # 事件循环
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
