#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, ListView, DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from zanhu.helpers import ajax_required
from zanhu.qa.models import Answer, Question
from zanhu.qa.forms import QuestionForm
from zanhu.notifications.views import notification_handler


class QuestionListView(LoginRequiredMixin, ListView):
    """所有的问题页"""
    # 绑定模型类
    model = Question
    # 绑定前端页面
    template_name = "qa/question_list.html"
    paginate_by = 10
    context_object_name = "questions"

    def get_context_data(self, *, object_list = None, **kwargs):
        """重写上下文对象"""
        context = super(QuestionListView, self).get_context_data()
        # 页面的标签功能
        context["popular_tags"] = Question.objects.get_counted_tags()
        # 需要选中一个type栏
        context["active"] = "all"
        return context


class AnsweredQuestionListView(QuestionListView):
    """已有采纳问题的答案，是对上面问题的进一步划分所以继承上面的问题列表页"""

    def get_queryset(self):
        """拿到已经被采纳的答案的问题"""
        return Question.objects.get_answered()

    def get_context_data(self, *, object_list = None, **kwargs):
        context = super(AnsweredQuestionListView, self).get_context_data()
        context["active"] = "answered"
        return context


class UnansweredQuestionListView(QuestionListView):
    """已有采纳问题的答案，是对上面问题的进一步划分所以继承上面的问题列表页"""

    def get_queryset(self):
        """拿到已经被采纳的答案的问题"""
        return Question.objects.get_unanswered()

    def get_context_data(self, *, object_list = None, **kwargs):
        context = super(UnansweredQuestionListView, self).get_context_data()
        context["active"] = "unanswered"
        return context

@method_decorator(cache_page(60 * 60), name = "get")
class CreateQuestionView(LoginRequiredMixin, CreateView):
    """用户提问"""
    # 绑定表单就是用户提出问题时需要填写的的数据需要post发送得到后台
    form_class = QuestionForm
    # 绑定前端模型
    template_name = "qa/question_form.html"
    message = "问题已经提交"

    def form_valid(self, form):
        """封装表单数据用的"""
        form.instance.user = self.request.user
        return super(CreateQuestionView, self).form_valid(form)

    def get_success_url(self):
        """创建成功后跳转的页面,先跳转到没有回答的问题页面"""
        messages.success(self.request, self.message)
        return reverse_lazy("qa:unanswered_q")


class QuestionDetailView(LoginRequiredMixin, DetailView):
    """问题详情页"""
    model = Question
    context_object_name = "question"
    template_name = "qa/question_detail.html"

@method_decorator(cache_page(60 * 60), name = "get")
class CreateAnswerView(LoginRequiredMixin, CreateView):
    """用户回答问题"""
    model = Answer
    # 单独一个字段对from表单进行处理
    fields = ["content"]
    message = "您的问题已经提交"
    template_name = "qa/answer_form.html"

    def form_valid(self, form):
        """封装表单"""
        form.instance.user = self.request.user
        form.instance.question_id = self.kwargs["question_id"]
        return super(CreateAnswerView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy("qa:question_detail", kwargs = {"pk": self.kwargs["question_id"]})


@login_required
@ajax_required
@require_http_methods(["POST"])
def question_vote(request):
    """用户给问题投票 Ajax post请求"""
    # 获取当前问题的主键
    question_id = request.POST["question"]
    # 获取用户是踩还是赞 "U"表示赞，"D"表示踩
    value = True if request.POST["value"] == "U" else False
    # 获取当前的问题模型类
    question = Question.objects.get(pk = question_id)
    # 获取当前对问题进行踩或者赞的用户
    users = question.votes.values_list("user", flat = True)

    # 简化的写法
    # 首先用户已经再赞过或者踩过的用户中并且用户有点了赞或者踩那么代表用户要么取消赞要么取消踩就需要删除记录
    if request.user.pk in users and (question.votes.get(user = request.user).value == value):
        question.votes.get(user = request.user).delete()
    else:
        # 这些就是用户赞或者踩需要创建
        question.votes.update_or_create(user = request.user, defaults = {"value": value})
    """
    # 1,用户首次操作，点赞/踩
    # 如果当前请求的用户不再点赞/踩的用户当中那么需要进行创建一个vote不管是踩的还是点赞的
    if request.user.pk not in users:
        # update_or_create有的话就更新，没有的话就删除
        question.votes.update_or_create(user = request.user, defaults = {"value": value})

    # 2,用户已经赞过需要取消赞或者踩一下问题
    elif question.votes.get(user = request.user).value:
        # 如果是赞的话取消赞，删除赞的记录
        if value:
            question.votes.get(user = request.user).delete()
        else:
            # 如果是踩的话那么更新踩过的记录
            question.votes.update_or_create(user = request.user, defaults = {"value": value})
    # 3,用户已经踩过取消踩或者赞一下
    else:
        if not value:
            # 此时是取消踩就是传来的还是false所以要删除踩的记录
            question.votes.get(user = request.user).delete()
        else:
            # 此时是需要赞一下传来的就是True那么直接赞一下更新记录
            question.votes.update_or_create(user = request.user, defaults = {"value": value})
    """
    # 把所有的票数返回回去
    return JsonResponse({"votes": question.total_votes()})


@login_required
@ajax_required
@require_http_methods(["POST"])
def answer_vote(request):
    """用户给回答投票 Ajax post请求"""
    answer_id = request.POST["answer"]
    value = True if request.POST["value"] == "U" else False
    answer = Answer.objects.get(uuid_id = answer_id)
    users = answer.votes.values_list("user", flat = True)

    # 简化的写法
    # 首先用户已经再赞过或者踩过的用户中并且用户有点了赞或者踩那么代表用户要么取消赞要么取消踩就需要删除记录
    if request.user.pk in users and (answer.votes.get(user = request.user).value == value):
        answer.votes.get(user = request.user).delete()
    else:
        # 这些就是用户赞或者踩需要创建
        answer.votes.update_or_create(user = request.user, defaults = {"value": value})
    return JsonResponse({"votes": answer.total_votes()})


@login_required
@ajax_required
@require_http_methods(["POST"])
def accept_answer(request):
    """
    接收回答，Ajax post请求
    已经接收的回答用户不能取消
    :param request:
    :return:
    """
    answer_id = request.POST["answer"]
    answer = Answer.objects.get(pk = answer_id)
    # 如果当前的用户不是提问者，抛出权限拒绝的错误
    if answer.question.user.username != request.user.username:
        raise PermissionDenied
    answer.accept_answer()
    # 当答案被接收时就通知回答者
    notification_handler(request.user, answer.user, "W", answer)
    return JsonResponse({"status": "true"})
