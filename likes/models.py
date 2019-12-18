from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
# Create your models here.

class LikeRecord(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	like_time = models.DateTimeField(auto_now_add=True)

	content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type','object_id')

class LikeCount(models.Model):
	like_num = models.IntegerField(default=0)

	content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type','object_id')

