# coding:UTF-8
import threading
from django.db import models
from django.template.loader import render_to_string
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from mysite.settings import EMAIL_HOST_USER
# Create your models here.

class SendEmail(threading.Thread):
	def __init__(self,subject,text,email,fail_silently=False):
		self.subject = subject
		self.text = text
		self.email = email
		self.fail_silently = fail_silently
		threading.Thread.__init__(self)


	def run(self):
		send_mail(
			self.subject,
			'',
			EMAIL_HOST_USER,
			[self.email],
			fail_silently = self.fail_silently,
			html_message = self.text,
		)





class Comment(models.Model):
	content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	text = models.TextField()
	date = models.DateTimeField(auto_now_add=True)

	#related_name区分指向同一模型的不同外键

	#author指向该条评论的作者，不得为空
	author = models.ForeignKey(User,related_name='comments',on_delete=models.CASCADE)
	#reply_to指向该条评论回复的评论的作者，可能为空（若该条评论为最上级评论）
	reply_to = models.ForeignKey(User,related_name='replies',null=True,on_delete=models.CASCADE)

	#parent指向该条评论回复的评论，可能为空（若该条评论就是最上级评论）
	parent = models.ForeignKey('self',related_name='parent_comment',null=True,on_delete=models.CASCADE)
	#root指向该条评论所对应的最顶级评论，可能为空（若该条评论就是最上级评论）
	root = models.ForeignKey('self',related_name='root_comment',null=True,on_delete=models.CASCADE)

	def send_email(self):
		#发送邮件
		#回复评论发送邮件
		if self.parent:
			if not self.reply_to.userconfig.is_email_active:
				return
			subject = '有人回复你的评论'
			email = self.reply_to.email
		#评论博客发送邮件
		else:
			if not self.content_object.get_user_config():
				return
			subject = '有人评论你的博客'
			email = self.content_object.get_email()		
		if email != '':
			context = {}
			context['text'] = self.text
			context['blog_url'] = self.content_object.get_url()
			text = render_to_string('comment/send_mail.html',context)
			send_email = SendEmail(subject,text,email)
			send_email.start()





	def __str__(self):
		return self.text

	class Meta:
		ordering = ["date",]