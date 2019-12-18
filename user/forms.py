from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from captcha.fields import CaptchaField,CaptchaTextInput
from.models import Profile

class LoginForm(forms.Form):
	username_or_email = forms.CharField(label='用户名或邮箱',widget=forms.TextInput(attrs={'class':'form-control',
																			'placeholder':'请输入用户名或邮箱'}))
	password = forms.CharField(label='密码',widget=forms.PasswordInput(attrs={'class':'form-control',
																			'placeholder':'请输入密码'}))
	captcha = CaptchaField(label='验证码',error_messages={'invalid':'验证码错误'} ,widget=CaptchaTextInput(attrs={'class':'form-control',
																			'placeholder':'请输入验证码'}))
	def clean(self):
		username_or_email = self.cleaned_data['username_or_email']
		password = self.cleaned_data['password']

		user = auth.authenticate(username = username_or_email,password = password)
		if user is None:
			if User.objects.filter(email=username_or_email).exists():
				username = User.objects.get(email=username_or_email).username
				user = auth.authenticate(username = username,password = password)
				if user:
					self.cleaned_data['user'] = user
					return self.cleaned_data
			raise forms.ValidationError('用户名或密码不正确')
		self.cleaned_data['user'] = user
		return self.cleaned_data

class RegForm(forms.Form):
	username = forms.CharField(label='用户名',min_length=3,max_length=30,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'请输入3到30位用户名'}))
	email = forms.EmailField(label='邮箱',widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'请输入邮箱'}))
	password = forms.CharField(label='密码',min_length=6,max_length=20,widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请输入6到20位密码'}))
	password_again = forms.CharField(label='重复密码',min_length=6,max_length=20,widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请再次输入密码'}))
	captcha = CaptchaField(label='验证码',error_messages={'invalid':'验证码错误'} ,widget=CaptchaTextInput(attrs={'class':'form-control',
																			'placeholder':'请输入验证码'}))
	validation_code = forms.CharField(label='邮箱验证码',required=False,widget=forms.TextInput(attrs={'class':'form-control',
																				'placeholder':'请输入发送到邮箱的验证码',}))
	def __init__(self,*args,**kwargs):
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super().__init__(*args,**kwargs)

	def clean_username(self):
		username = self.cleaned_data['username']
		if User.objects.filter(username=username).exists():
			raise forms.ValidationError('用户名已经存在')
		else:
			return username 

	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('邮箱已被使用')
		else:
			return email

	def clean_password_again(self):
		password = self.cleaned_data['password']
		password_again = self.cleaned_data['password_again']
		if password_again != password:
			raise forms.ValidationError('两次输入密码不一致')
		else:
			return password_again

	def clean_validation_code(self):
		validation_code = self.cleaned_data.get('validation_code','')
		if validation_code == '' or validation_code!=self.request.session['register']:
			raise forms.ValidationError('验证码错误')
		return validation_code

class ChangeNicknameForm(forms.Form):
	new_nickname = forms.CharField(label='新昵称',max_length=20,widget=forms.TextInput(attrs={'class':'form-control',
																								'placeholder':'请输入新昵称'}))

	def __init__(self,*args,**kwargs):
		if 'user' in kwargs:
			self.user = kwargs.pop('user')
		super().__init__(*args,**kwargs)

	def clean_new_nickname(self):
		user = self.user
		if user.is_authenticated:
			self.cleaned_data['user'] = user
		else:
			raise forms.ValidationError('用户未登录')

		new_nickname = self.cleaned_data.get('new_nickname','').strip()
		profile,created = Profile.objects.get_or_create(user=user)
		if profile.nickname == new_nickname:
			raise forms.ValidationError('新昵称与原昵称相同')
		else:
			return new_nickname

class BindEmailForm(forms.Form):
	email = forms.EmailField(label='邮箱地址',widget=forms.EmailInput(attrs={'class':'form-control',
																			'placeholder':'请输入合法的邮箱地址'}))
	validation_code = forms.CharField(label='验证码',required=False,widget=forms.TextInput(attrs={'class':'form-control',
																				'placeholder':'请输入验证码',}))

	def __init__(self,*args,**kwargs):
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super().__init__(*args,**kwargs)

	def clean_email(self):
		email = self.cleaned_data.get('email','')
		if email == '':
			raise forms.ValidationError('邮箱为空')
		if self.request.user.email != '':
			raise forms.ValidationError('用户已绑定邮箱')
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('邮箱已经绑定其他账号')
		return email

		
	def clean_validation_code(self):
		validation_code = self.cleaned_data.get('validation_code','')
		user = self.request.user
		if not user.is_authenticated:
			raise forms.ValidationError('用户未登录')
		if validation_code == '' or validation_code!=self.request.session['bind_email']:
			raise forms.ValidationError('验证码错误')
		return validation_code

class ChangePasswordForm(forms.Form):
	old_password = forms.CharField(label='原密码',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请输入原密码'}))
	new_password = forms.CharField(label='新密码',min_length=6,max_length=20,widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请输入6到20位新密码'}))
	new_password_again = forms.CharField(label='再次输入新密码',min_length=6,max_length=20,widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请再次输入新密码'}))
	
	def __init__(self,*args,**kwargs):
		if 'user' in kwargs:
			self.user = kwargs.pop('user')
		super().__init__(*args,**kwargs)

	def clean_old_password(self):
		old_password = self.cleaned_data.get('old_password','')
		if not self.user.check_password(old_password):
			raise forms.ValidationError('原密码错误')
		return old_password

	def clean(self):
		new_password = self.cleaned_data.get('new_password','')
		old_password = self.cleaned_data.get('old_password','')
		new_password_again = self.cleaned_data.get('new_password_again','')
		if new_password!=new_password_again or new_password == '':
			raise forms.ValidationError('两次输入密码不一致')
		if new_password == old_password and new_password!='':
			raise forms.ValidationError('新密码不能与原密码相同')
		return self.cleaned_data


class ResetPasswordForm(forms.Form):
	email = forms.EmailField(label='邮箱',widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'请输入邮箱'}))
	new_password = forms.CharField(label='新密码',min_length=6,max_length=20,widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请输入6到20位新密码'}))
	new_password_again = forms.CharField(label='再次输入新密码',min_length=6,max_length=20,widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请再次输入新密码'}))
	validation_code = forms.CharField(label='验证码',required=False,widget=forms.TextInput(attrs={'class':'form-control',
																			'placeholder':'请输入验证码',}))

	def __init__(self,*args,**kwargs):
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super().__init__(*args,**kwargs)

	def clean_email(self):
		email = self.cleaned_data['email']
		if not User.objects.filter(email=email).exists():
			raise forms.ValidationError('邮箱错误')
		user = User.objects.get(email=email)
		self.cleaned_data['user'] = user
		return email

	def clean_validation_code(self):
		validation_code = self.cleaned_data.get('validation_code','')
		if validation_code == '' or validation_code!=self.request.session['reset_password_code']:
			raise forms.ValidationError('验证码错误')
		return validation_code

	def clean(self):
		new_password = self.cleaned_data['new_password']
		new_password_again = self.cleaned_data.get('new_password_again','')
		if new_password_again != new_password:
			raise forms.ValidationError('两次输入的密码不一致')
		if new_password_again == '' and new_password == '':
			raise forms.ValidationError('密码不得为空')
		user = self.cleaned_data.get('user','')
		if user != '':
			if user.check_password(new_password):
				raise forms.ValidationError('新密码与原密码相同')
		return self.cleaned_data




