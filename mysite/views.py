# coding:UTF-8
import pickle
from django.shortcuts import render
from django_redis import get_redis_connection
from django.contrib.contenttypes.models import ContentType
from read_statistics.utils import get_read_details_of_past_seven_days,get_today_hot_data,get_yesterday_hot_data,get_seven_days_hot_data
from blog.models import Blog

def home(request):
	content_type = ContentType.objects.get_for_model(Blog)
	dates,read_nums = get_read_details_of_past_seven_days(content_type)

	#使用缓存获取数据

	conn = get_redis_connection('default')
	hot_blogs_of_seven_days = conn.get('hot_blogs_of_seven_days')
	if hot_blogs_of_seven_days is None:
		print ("not use cache")
		hot_blogs_of_seven_days = get_seven_days_hot_data()
		conn.setex('hot_blogs_of_seven_days',60*60,pickle.dumps(hot_blogs_of_seven_days))
	else:
		print("use cache")
		hot_blogs_of_seven_days = pickle.loads(hot_blogs_of_seven_days)


	context = {}
	context['read_nums'] = read_nums
	context['dates'] = dates
	context['today_hot_data'] = get_today_hot_data(content_type)
	context['yesterday_hot_data'] = get_yesterday_hot_data(content_type)
	context['hot_blogs_of_seven_days'] = hot_blogs_of_seven_days
	return render(request,'home.html',context)