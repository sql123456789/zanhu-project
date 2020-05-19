#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from django import forms
from zanhu.qa.models import Question
from markdownx.fields import MarkdownxFormField


class QuestionForm(forms.ModelForm):
    """问答模块的表单类用来处理form表单请求"""

    # 内容
    content = MarkdownxFormField()
    status = forms.CharField(widget = forms.HiddenInput())  # 隐藏标签

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "status"]
