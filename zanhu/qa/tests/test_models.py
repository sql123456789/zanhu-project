#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from test_plus.test import TestCase
from zanhu.qa.models import Question, Answer


class QAModelsTest(TestCase):
    def setUp(self):
        """初始化操作"""
        # 创建两个用户
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")
        #创建两个问题
        self.question_one = Question.objects.create(
            user = self.user,
            title = "问题1",
            content = "问题1的内容",
            tags = "测试1, 测试2"
        )

        self.question_two = Question.objects.create(
            user = self.user,
            title = "问题2",
            content = "问题1的内容",
            has_answer = True,
            tags = "测试1,测试2"
        )
        # 给问题2创建一个正确的回答
        self.answer = Answer.objects.create(
            user = self.user,
            question = self.question_two,
            content = "问题2的正确回答",
            is_answer = True
        )

    def test_can_vote_question(self):
        """给问题投票"""
        # user1和user2各自给问题2有一票
        self.question_one.votes.update_or_create(user=self.user, defaults={"value":True})
        self.question_one.votes.update_or_create(user=self.other_user, defaults={"value":True})
        # 判断此时的问题1的票数是否为2票
        assert self.question_one.total_votes() == 2

    def test_can_vote_answer(self):
        """给答案投票"""
        self.answer.votes.update_or_create(user=self.user, defaults={"value":True})
        self.answer.votes.update_or_create(user=self.other_user, defaults={"value":True})
        assert self.answer.total_votes() == 2

    def test_get_question_voters(self):
        """问题投票的用户"""
        # user1给问题1点赞
        self.question_one.votes.update_or_create(user=self.user, defaults={"value":True})
        # user2给问题2踩
        self.question_one.votes.update_or_create(user=self.other_user, defaults={"value":False})
        # 判断此时的user1是否再点赞的用户当中
        assert self.user in self.question_one.get_upvoters()
        # 判断此时user2是否再踩的用户中
        assert self.other_user in self.question_one.get_downvoters()

    def test_get_answer_voters(self):
        """回答投票的用户"""
        self.answer.votes.update_or_create(user=self.user, defaults={"value":True})
        self.answer.votes.update_or_create(user=self.other_user,defaults={"value":False})
        assert self.user in self.answer.get_upvoters()
        assert self.other_user in self.answer.get_downvoters()

    def test_unanswered_question(self):
        """未被回答的问题"""
        assert self.question_one == Question.objects.get_unanswered()[0]

    def test_answered_question(self):
        """已有被采纳答案的问题"""
        assert self.question_two == Question.objects.get_answered()[0]

    def test_question_get_answers(self):
        """获取问题的所有回答"""
        assert self.answer == self.question_two.get_answers()[0]
        assert self.question_two.count_answers() == 1

    def test_question_accepted_answer(self):
        """提问者接收回答"""
        # 给问题1创建3回答
        answer_one = Answer.objects.create(
            user = self.user,
            question = self.question_one,
            content = "回答1"
        )
        answer_two= Answer.objects.create(
            user = self.user,
            question = self.question_one,
            content = "回答2"
        )
        answer_three = Answer.objects.create(
            user = self.user,
            question = self.question_one,
            content = "回答3"
        )
        # 此时三个答案都不是被接受的答案
        self.assertFalse(answer_one.is_answer)
        self.assertFalse(answer_two.is_answer)
        self.assertFalse(answer_three.is_answer)
        # 问题1没有被接受的答案所以此时has_answer是false
        self.assertFalse(self.question_one.has_answer)
        # 接受回答1 为正确答案
        answer_one.accept_answer()

        self.assertTrue(answer_one.is_answer)
        self.assertFalse(answer_two.is_answer)
        self.assertFalse(answer_three.is_answer)
        # 此时问题1已经有人正确的答案
        self.assertTrue(self.question_one.has_answer)

    def test_question_str_(self):
        assert isinstance(self.question_one, Question)
        assert str(self.question_one) == "问题1"

    def test_answer_str_(self):
        assert isinstance(self.answer, Answer)
        assert str(self.answer) == "问题2的正确回答"



