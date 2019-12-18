# coding:UTF-8
from django.shortcuts import render
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from read_statistics.utils import get_read_details_of_past_seven_days,get_today_hot_data,get_yesterday_hot_data,get_seven_days_hot_data
from blog.models import Blog

def home(request):
	content_type = ContentType.objects.get_for_model(Blog)
	dates,read_nums = get_read_details_of_past_seven_days(content_type)

	#使用缓存获取数据
	hot_blogs_of_seven_days = cache.get('hot_blogs_of_seven_days')
	print(hot_blogs_of_seven_days)
	if hot_blogs_of_seven_days is None:
		hot_blogs_of_seven_days = get_seven_days_hot_data()
		cache.set('hot_blogs_of_seven_days',hot_blogs_of_seven_days,3600)

	context = {}
	context['read_nums'] = read_nums
	context['dates'] = dates
	context['today_hot_data'] = get_today_hot_data(content_type)
	context['yesterday_hot_data'] = get_yesterday_hot_data(content_type)
	context['hot_blogs_of_seven_days'] = hot_blogs_of_seven_days
	return render(request,'home.html',context)

