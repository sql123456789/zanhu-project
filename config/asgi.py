#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

import os
import sys
import django
from pathlib import Path
from channels.routing import get_default_application

# 将应用application加入到查找路径中
app_path = Path(__file__).parents[1].resolve()
# 应用再下面这个路径中 ../zanhu/zanhu
sys.path.append(str(app_path / "zanhu"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()
application = get_default_application()
