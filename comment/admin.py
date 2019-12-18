from django.contrib import admin
from .models import Comment
# Register your models here.
@admin.register(Comment)
class AdminComment(admin.ModelAdmin):
    list_display = ("id","content_type","author","date","text",)