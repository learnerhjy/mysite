from django.contrib import admin
from .models import LikeRecord,LikeCount
# Register your models here.
@admin.register(LikeRecord)
class AdminLikeRecord(admin.ModelAdmin):
    list_display = ("id","content_type","user","like_time")

@admin.register(LikeCount)
class AdminLikeCount(admin.ModelAdmin):
    list_display = ("id","content_type","like_num")
