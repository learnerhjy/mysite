#coding:UTF-8
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from .models import LikeRecord,LikeCount

def SuccessResponse(like_num):
	data = {}
	data['status'] = 'SUCCESS'
	data['like_num'] = like_num
	return JsonResponse(data)

def ErrorResponse(code,message):
	data = {}
	data['status'] = 'ERROR'
	data['code'] = code
	data['message'] = message
	return JsonResponse(data)

def like_change(request):
	user = request.user
	if not user.is_authenticated:
		return ErrorResponse('399','no login')

	content_type = request.GET.get('content_type')
	object_id = int(request.GET.get('object_id'))
	try:
		content_type = ContentType.objects.get(model=content_type)
		model_class = content_type.model_class()
		model_obj = model_class.objects.get(pk=object_id)
	except ObjectDoesNotExist:
		return ErrorResponse('400','object does not exist')


	is_liked = request.GET.get('is_liked')

	if is_liked == "true":
		# 进行点赞
		like_record,created = LikeRecord.objects.get_or_create(content_type=content_type,object_id=object_id,user=user)
		if created:
			# 未点赞，可以点赞
			like_count,created = LikeCount.objects.get_or_create(content_type=content_type,object_id=object_id)
			like_count.like_num += 1
			like_count.save()
			return SuccessResponse(like_count.like_num)
		else:
			# 已经点赞过，不能重复点赞
			return ErrorResponse(401,'you have already liked')

	else:
		if LikeRecord.objects.filter(content_type=content_type,object_id=object_id,user=user).exists():
			# 取消点赞
			like_record = LikeRecord.objects.get(content_type=content_type,object_id=object_id,user=user)
			like_record.delete()
			like_count,created = LikeCount.objects.get_or_create(content_type=content_type,object_id=object_id)
			if not created:
				#有点赞数，取消点赞
				like_count.like_num -= 1
				like_count.save()
				return SuccessResponse(like_count.like_num)
			else:
				#没有点赞过，不能取消点赞
				return ErrorResponse(402,'you can not cancel as you do not like')
		else:
			#无点赞记录，数据出错
			return ErrorResponse(403,'data error')

