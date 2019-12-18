import datetime
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.utils import timezone
from .models import ReadNum,ReadDetail
from blog.models import Blog


def read_statistics_read_once(request,obj):
    key = 'read_num_of_%s'%obj.pk
    if not request.COOKIES.get(key):
        ct = ContentType.objects.get_for_model(obj)
        '''
        if ReadNum.objects.filter(content_type=ct,object_id=obj.pk):
            readnum = ReadNum.objects.get(content_type=ct,object_id=obj.pk)
        else:
            readnum = ReadNum(content_type=ct,object_id=obj.pk)
        '''
        readNum,created = ReadNum.objects.get_or_create(content_type=ct,object_id=obj.pk)
        readNum.read_num +=1
        readNum.save()

        readDetail,created = ReadDetail.objects.get_or_create(content_type=ct,object_id=obj.pk,read_date=timezone.now().date())
        readDetail.read_num +=1
        readDetail.save()
    return key

def get_read_details_of_past_seven_days(content_type):
    read_nums = []
    dates = []
    today = timezone.now().date()
    for i in range(6,-1,-1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type,read_date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
    return dates,read_nums

def get_today_hot_data(content_type):
    today = timezone.now().date()
    today_hot_data = ReadDetail.objects.filter(content_type=content_type,read_date=today).order_by('-read_num')
    return today_hot_data[:7]

def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_hot_data = ReadDetail.objects.filter(content_type=content_type,read_date=yesterday).order_by('-read_num')
    return yesterday_hot_data[:7]

def get_seven_days_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    hot_blogs_of_seven_days = Blog.objects.filter(read_details__read_date__lt=today,read_details__read_date__gte=date)\
                                          .values('pk','title')\
                                          .annotate(read_num_sum=Sum('read_details__read_num'))
    return hot_blogs_of_seven_days
