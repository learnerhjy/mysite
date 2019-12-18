from django.contrib import admin
from .models import BlogType,Blog
# Register your models here.

@admin.register(Blog)
class AdminBlog(admin.ModelAdmin):
    list_display = ("pk","title","blog_type","author","get_read_num","create_time","last_updated_time")

@admin.register(BlogType)
class AdminBlogType(admin.ModelAdmin):
    list_display = ("pk","type_name")

