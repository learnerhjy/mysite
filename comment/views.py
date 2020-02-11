# coding:UTF-8
from django.shortcuts import render,redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.http import JsonResponse
from .models import Comment
from .forms import CommentForm


def update_comment(request):
	data = {}
	comment_form = CommentForm(request.POST,user=request.user)
	referer = request.META.get('HTTP_REFERER',reverse('home'))
	#检查通过
	if comment_form.is_valid():
		comment = Comment()
		comment.author = comment_form.cleaned_data['user']
		comment.text = comment_form.cleaned_data['text']
		comment.content_object = comment_form.cleaned_data['content_object']

		parent = comment_form.cleaned_data['parent']
		if not parent is None:
			comment.root = parent.root if not parent.root is None else parent
			comment.parent = parent 
			comment.reply_to = parent.author
		comment.save()	

		comment.send_email()

		data['status'] = 'SUCCESS'
		data['username'] = comment.author.get_username_or_nickname()
		data['date'] = comment.date.strftime('%Y-%m-%d %H:%M:%S')
		#data['date'] = '刚刚'
		data['text'] = comment.text
		data['content_type'] = ContentType.objects.get_for_model(comment).model
		if not parent is None:
			data['reply_to'] = parent.author.username
		else:
			data['reply_to'] = ''
		data['pk'] = comment.pk
		data['root_pk'] = comment.root.pk if not comment.root is None else ""
	else:
		#return render(request,'error.html',{'message':comment_form.errors,'redirect_to':referer})
		data['status'] = 'ERROR'
		data['message'] = list(comment_form.errors.values())[0][0]
	return JsonResponse(data)	
