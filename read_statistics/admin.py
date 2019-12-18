from django.contrib import admin
from .models import ReadNum,ReadDetail

@admin.register(ReadNum)
class AdminReadNum(admin.ModelAdmin):
    list_display = ("read_num","content_type","object_id")

@admin.register(ReadDetail)
class AdminReadDetail(admin.ModelAdmin):
    list_display = ("read_num","read_date","content_type","object_id")