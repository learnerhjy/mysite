#coding:UTF-8
from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from mysite.settings import NUMBER_OF_BLOGS_PER_PAGE
from read_statistics.utils import read_statistics_read_once
from .models import Blog,BlogType
from comment.models import Comment
from comment.forms import CommentForm
# Create your views here.
def get_blog_common_data(request,blogs_all_list):
	paginator = Paginator(blogs_all_list,NUMBER_OF_BLOGS_PER_PAGE) #分页器，每一页NUMBER_OF_BLOGS_PER_PAGE篇blog
	page_num = request.GET.get('page',1) #从GET请求获得页面参数，若无则为1
	page_of_blogs = paginator.get_page(page_num) #从分页器获取page_num页的所有blog
	current_page_num = page_of_blogs.number #当前页面
	page_range = list(range(max(1,current_page_num-2),min(paginator.num_pages,current_page_num+2)+1))

	if paginator.num_pages!=1:
	#显示首页和尾页
		if page_range[0]!=1:
			page_range.insert(0,1)
		if page_range[-1]!=paginator.num_pages:
			page_range.append(paginator.num_pages)
	#加入...
		if page_range[1]-1>1:
			page_range.insert(1,'...')
		if paginator.num_pages-page_range[-2]>1:
			page_range.insert(-1,'...')

	#blog_types = BlogType.objects.all()

	#显示博客分类中每一分类对应的博客数
	blog_types = BlogType.objects.annotate(blog_count=Count('blog'))
	#显示日期归档中每一日期所对应的博客数
	blog_dates_list={}
	for blog_date in Blog.objects.dates('create_time','month',order='DESC'):
		blog_dates_list[blog_date] = Blog.objects.all().filter(	create_time__year=blog_date.year,
																create_time__month=blog_date.month).count()
	blog_dates = Blog.objects.dates('create_time','month',order='DESC')
	context = {}
	context['page_of_blogs'] = page_of_blogs
	context['page_range'] = page_range
	context['blog_dates'] = blog_dates_list
	context['blog_types'] = blog_types
	return context

def blog_list(request):
	blogs_all_list = Blog.objects.all() #获取所有blog
	context = get_blog_common_data(request,blogs_all_list)
	return render(request,'blog/blog_list.html',context)

def blog_detail(request,blog_pk):
    blog = get_object_or_404(Blog,pk=blog_pk)

    read_cookie_key=read_statistics_read_once(request,blog)

    #blog_content_type = ContentType.objects.get_for_model(blog)
    #comments = Comment.objects.filter(object_id=blog.pk,content_type = blog_content_type,root=None)

    previous_blog = Blog.objects.filter(create_time__gt=blog.create_time).last()
    next_blog = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context = {}
    context['blog'] = blog
    context['previous_blog'] = previous_blog
    context['next_blog'] = next_blog
    context['user'] = request.user
    #context['comments'] = comments.order_by('-date')
    #context['comment_form'] = CommentForm(initial={'content_type':blog_content_type.model,'object_id':blog.pk,'reply_comment_id':0})
    response = render(request,'blog/blog_detail.html',context)
    response.set_cookie(read_cookie_key,'true')
    return response
    
def blogs_with_type(request,type_pk):
	type_name = get_object_or_404(BlogType,pk=type_pk)
	blogs_all_list = Blog.objects.filter(blog_type=type_name) #获取所有blog
	context = get_blog_common_data(request,blogs_all_list)
	context['type_name'] = type_name
	return render(request,'blog/blogs_with_type.html',context)

def blogs_with_date(request,year,month):
	blogs_all_list = Blog.objects.filter(create_time__year = year,create_time__month=month) #获取所有blog
	context = get_blog_common_data(request,blogs_all_list)
	context['blog_date'] = '%s年%s月'%(year,month)
	return render(request,'blog/blogs_with_date.html',context)
















