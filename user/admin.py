from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile,UserConfig



class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserConfigInline(admin.StackedInline):
    model = UserConfig
    can_delete = False

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,UserConfigInline,)
    list_display = ('username','nickname','email','is_active','is_staff','is_superuser','is_email_active')
    def nickname(self,obj):
    	return obj.profile.nickname
    nickname.short_description = '昵称'

    def is_email_active(self,obj):
    	return obj.userconfig.is_email_active
    is_email_active.short_description = '是否启用邮件通知'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user','nickname',)

@admin.register(UserConfig)
class UserConfigAdmin(admin.ModelAdmin):
	list_display = ('user','is_email_active',)
