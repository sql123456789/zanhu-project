#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from django import forms
from zanhu.articles.models import Articles
from markdownx.fields import MarkdownxFormField


class ArticleForm(forms.ModelForm):
    """用来处理form表单请求"""

    content = MarkdownxFormField()
    status = forms.CharField(widget = forms.HiddenInput())  # 隐藏标签
    # 已经有默认值了就不需要用户填写
    edited = forms.BooleanField(widget = forms.HiddenInput(), initial = False, required = False)

    class Meta:
        model = Articles
        fields = ["title", "content", "image", "tags", "status", "edited"]
