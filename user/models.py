from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	nickname = models.CharField(max_length=20,verbose_name='昵称')

	def __str__(self):
		return '<Profile:%s for %s>'%(self.nickname,self.user.username)

class UserConfig(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	is_email_active = models.BooleanField(default=False,verbose_name='是否启用邮件通知')

	def __str__(self):
		return '<UserConfig:%s for %s>'%('true' if self.is_email_active else 'false',self.user.username)

def get_username_or_nickname(self):
	if Profile.objects.filter(user=self).exists():
		nickname = self.profile.nickname
		return nickname
	return self.username

def get_nickname(self):
	nickname = ''
	if Profile.objects.filter(user=self).exists():
		nickname = self.profile.nickname
	return nickname

User.get_nickname = get_nickname
User.get_username_or_nickname = get_username_or_nickname