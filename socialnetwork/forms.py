from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from socialnetwork.models import *
from django.forms.widgets import FileInput
from django.forms import ModelForm, FileInput





class LoginForm(forms.Form):
	username = forms.CharField(max_length = 20)
	password = forms.CharField(max_length = 200, widget = forms.PasswordInput())

	# Customizes form validation for properties that apply to more
	# than one field.  Overrides the forms.Form.clean function.
	def clean(self):
		# Calls our parent (forms.Form) .clean function, gets a dictionary
		# of cleaned data as a result
		cleaned_data = super().clean()

		# Confirms that the two password fields match
		username = cleaned_data.get('username')
		password = cleaned_data.get('password')
		user = authenticate(username=username, password=password)
		if not user:
			raise forms.ValidationError("Invalid username/password")

		# We must return the cleaned data we got from our parent.
		return cleaned_data

class RegistrationForm(forms.Form):
	username   = forms.CharField(max_length = 20)
	password  = forms.CharField(max_length = 200,
								 label='Password',
								 widget = forms.PasswordInput())
	confirm_password  = forms.CharField(max_length = 200,
								 label='Confirm password',
								 widget = forms.PasswordInput())

	email      = forms.CharField(max_length=50,
								 widget = forms.EmailInput())
	first_name = forms.CharField(max_length=20)
	last_name  = forms.CharField(max_length=20)

	# Customizes form validation for properties that apply to more
	# than one field.  Overrides the forms.Form.clean function.
	def clean(self):
		# Calls our parent (forms.Form) .clean function, gets a dictionary
		# of cleaned data as a result
		cleaned_data = super().clean()

		# Confirms that the two password fields match
		password = cleaned_data.get('password')
		confirm_password = cleaned_data.get('confirm_password')
		if password and confirm_password and password != confirm_password:
			raise forms.ValidationError("Passwords did not match.")

		# We must return the cleaned data we got from our parent.
		return cleaned_data


	# Customizes form validation for the username field.
	def clean_username(self):
		# Confirms that the username is not already present in the
		# User model database.
		username = self.cleaned_data.get('username')
		if User.objects.filter(username__exact=username):
			raise forms.ValidationError("Username is already taken.")

		# We must return the cleaned data we got from the cleaned_data
		# dictionary
		return username

class ProfileForm(forms.ModelForm):
	MAX_UPLOAD_SIZE = 2500000
	class Meta:
		model = Profile
		fields = ( 'profile_picture', 'bio_input_text')

	def clean(self):
		cleaned_data = super(ProfileForm,self).clean()
		return cleaned_data

	def clean_picture(self):
		profile_picture = self.cleaned_data['profile_picture']
		if not profile_picture:
			raise forms.ValidationError('You must upload a picture')
		if not profile_picture.content_type or not profile_picture.content_type.startswith('image'):
			raise forms.ValidationError('File type is not image')
		if profile_picture.size > MAX_UPLOAD_SIZE:
			raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
		return profile_picture
class AddPostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = {'post_input_text',}
	# post = forms.CharField(max_length = 160)
	# def clean(self):
	# 	cleaned_data = super(AddPostForm,self).clean()
	# 	return cleaned_data

	# def clean_post(self):
	# 	cleaned_data = self.cleaned_data.get('post_input_text')
	# 	if not cleaned_data:
	# 		raise forms.ValidationError("You must use post method")
	# 	if len(cleaned_data) == 0:
	# 		raise forms.ValidationError("You must write a post first")
	# 	if len(cleaned_data) >200:
	# 		raise forms.ValidationError("Your post should be within 200 characters")
	# 	return cleaned_data
class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = {'comment_input_text',}
	# item = forms.CharField(max_length = 200)
	# def clean(self):
	#     cleaned_data = super(CommentForm,self).clean()
	#     return cleaned_data
	# def clean_comment(self):
	#     cleaned_data = self.cleaned_data.get(' comment_input_text')
	#     if not cleaned_data:
	#         raise forms.ValidationError("need to use post method")
	#     if len(cleaned_data) == 0:
	#         raise forms.ValidationError("You must write a comment first")
	#     if len(cleaned_data) >200:
	#         raise forms.ValidationError("Your comment should be within 200 characters")
	#     return cleaned_data
