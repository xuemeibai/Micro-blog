from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import datetime,timezone
from socialnetwork.forms import *
from django.http import HttpResponse, Http404
from socialnetwork.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.dateparse import parse_datetime
import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def globalStream_action(request):
	context={}
	profile = get_object_or_404(Profile,user=request.user)
	form =  ProfileForm(instance=profile)
	items = Post.objects.all().order_by("date_created").reverse()
	context['newpost'] = AddPostForm()
	context['items'] = items
	context['user'] = request.user
	context['profile'] = profile
	context['form'] = form
	return render(request, 'socialnetwork/globalStream.html', context)


@login_required
def followerStream_action(request):

	context={}
	profile = get_object_or_404(Profile,id=request.user.id)
	form = ProfileForm(instance=profile)
	followings= Profile.objects.get(user = request.user).following.all()
	items = Post.objects.filter(user__in=followings)
	items = items.order_by("date_created").reverse()
	context['newpost'] = AddPostForm()
	context['items'] = items
	context['user'] = request.user
	context['profile'] = profile
	context['form'] = form
	context['identity'] = request.user
	return render(request, 'socialnetwork/followerStream.html', context)

@login_required
def profiles_action(request,id):
	errors=[]
	context={}
	context['errors'] = errors
	identity = get_object_or_404( User, id = id )
	userprofile = get_object_or_404(Profile,id=request.user.id)
	profile = get_object_or_404(Profile,id=id)
	new_form = ProfileForm(instance=profile)
	# followings = profile.following.values_list("id",flat=True).distinct()
	# followings= Profile.objects.filter(user__in=profile.following)
	followings= Profile.objects.get(user = request.user).following.all()
	# items = Post.objects.filter(user = identity)
	# items = items.order_by("date_created").reverse()
	context['profile'] = profile
	context['form'] = new_form
	# context['items']= items
	context['identity'] = identity
	context['user'] = request.user
	context['userprofile'] = userprofile.following.all()
	context['followings'] = followings
	return render(request, 'socialnetwork/profiles.html', context)


def login_action(request):
	context = {}

	# Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['form'] = LoginForm()
		return render(request, 'socialnetwork/login.html', context)

	# Creates a bound form from the request POST parameters and makes the
	# form available in the request context dictionary.
	form = LoginForm(request.POST)
	context['form'] = form

	# Validates the form.
	if not form.is_valid():
		return render(request, 'socialnetwork/login.html', context)

	new_user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])

	login(request, new_user)
	return redirect(reverse('globalStream'))

def logout_action(request):
	logout(request)
	return redirect(reverse('login'))

def register_action(request):
	context = {}

	# Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['form'] = RegistrationForm()
		return render(request, 'socialnetwork/register.html', context)

	# Creates a bound form from the request POST parameters and makes the
	# form available in the request context dictionary.
	form = RegistrationForm(request.POST)
	context['form'] = form

	# Validates the form.
	if not form.is_valid():
		return render(request, 'socialnetwork/register.html', context)

	# At this point, the form data is valid.  Register and login the user.
	new_user = User.objects.create_user(username=form.cleaned_data['username'],
										password=form.cleaned_data['password'],
										email=form.cleaned_data['email'],
										first_name=form.cleaned_data['first_name'],
										last_name=form.cleaned_data['last_name'])
	new_user.save()
	profile = Profile(user=new_user, id=new_user.id)
	profile.save()
	new_user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])

	login(request, new_user)
	return redirect(reverse('globalStream'))

def edit_profile(request):
	context={}
	profile = Profile.objects.get(user = request.user)
	# newprofile=Profile()
	# newprofile.user=profile.user
	# newprofile.id=profile.id
	# profile.profile_picture.delete()
	# if request.method == 'GET':
	#   new_form = ProfileForm(instance=profile)
	#   context = { 'profile': profile, 'form': new_form }
	#   all_items = Post.objects.order_by("date_created").reverse()
	#   context['items'] = all_items
	#   context['user'] = request.user
	#   context['profile'] = profile
	#   context['form'] = new_form
	#   context['newpost'] = AddPostForm()
	#   return render(request, 'socialnetwork/profiles.html', context)
	new_form = ProfileForm(request.POST, request.FILES, instance = profile)
	if not new_form.is_valid():
		context = {'form': new_form, 'profile': profile}
		context['user'] = request.user
		context['form'] = new_form
		context['newpost'] = AddPostForm()
		context['profile']=profile
		return render(request, 'socialnetwork/profiles.html', context)
	if 'profile_picture' in request.FILES:
		#pic = new_form.cleaned_data['profile_picture']
		new_form.profile_picture = request.FILES['profile_picture']
		new_form['profile_picture'].content_type = new_form.cleaned_data['profile_picture'].content_type
	#print('Uploaded profile_picture: {} (type={})'.format(pic, type(pic)))
		
	# profile.save()
	new_form.save()
	context['profile']=profile
	context['form']=new_form
	context['user'] = request.user
	context['newpost'] = AddPostForm()
	context['identity'] = request.user
	return render(request, 'socialnetwork/profiles.html', context)


def get_photo(request, id):
	item = get_object_or_404(Profile, id=id)
	print('profile_picture #{} fetched from db: {} (type={})'.format(id, item.profile_picture, type(item.profile_picture)))
	# Maybe we don't need this check as form validation requires a profile_picture be uploaded.
	# But someone could have delete the profile_picture leaving the DB with a bad references.
	if not item.profile_picture:
		raise Http404

	return HttpResponse(item.profile_picture, content_type=item.content_type)


@login_required
def follow(request,id):
	errors=[]
	context={}
	profile=Profile.objects.get(id = id)
	userprofile = get_object_or_404(Profile,id=request.user.id)
	following_user = get_object_or_404(User,id = id)
	userprofile.following.add(following_user)
	userprofile.save()

	context['errors'] = errors
	items = Post.objects.filter(user = following_user)
	items = Post.objects.order_by("date_created").reverse()
	context['items']= items
	context['user'] = request.user
	context['profile'] = profile
	context['userprofile'] = userprofile.following.all()
	return render(request, 'socialnetwork/profiles.html', context)


@login_required
def unfollow(request,id):
	errors=[]
	context={}
	profile=Profile.objects.get(id = id)
	userprofile = get_object_or_404(Profile,id=request.user.id)
	following_user = get_object_or_404(User,id = id)
	userprofile.following.remove(following_user)
	userprofile.save()

	context['errors'] = errors
	items = Post.objects.filter(user = following_user)
	items = Post.objects.order_by("date_created").reverse()
	context['items']= items
	context['user'] = request.user
	context['profile'] = profile
	context['userprofile'] = userprofile.following.all()
	followings= Profile.objects.get(user = request.user).following.all()
	return render(request, 'socialnetwork/profiles.html', context)


@login_required


def add_comment(request):
	errors = []
	if not 'item' in request.POST or not request.POST['item']:
		message = 'You must enter a comment.'
		json_error = '{ "error": "'+ message +'" }'
		return HttpResponse(json_error, content_type='application/json')
	post = get_object_or_404(Post,id = request.POST.get('id'))

	new_comment = Comment(comment_input_text= request.POST.get('item'),user= request.user, date_created=datetime.now(timezone.utc),post = post)
	print(new_comment.date_created)
	new_comment.save()
	result=refresh_global(request)
	return result

@login_required


def add_post(request):
	errors = []
	# print(request.POST)
	if not 'item' in request.POST or not request.POST['item']:
		# print("error")
		message = 'You must enter a post.'
		json_error = '{ "error": "'+ message +'" }'
		return HttpResponse(json_error, content_type='application/json')
	new_post = Post(post_input_text= request.POST['item'],user= request.user, date_created=timezone.now())
	new_post.save()
	result=refresh_global(request)
	return result


@login_required

def refresh_global(request):
	if request.method=="GET":
		last_refresh="1970-01-01T00:00:01.988Z"
	elif request.method=='POST':
		last_refresh=request.POST['last_refresh']
	else:
		raise Http404
	posts=[]
		# posts = Post.objects.filter(date_created=parse_datetime(request.GET['last_refresh'])).reverse()
		# comments=Comment.objects.filter(date_created=parse_datetime(request.GET['last_refresh'])).reverse()
	for post in Post.objects.filter(date_created__gte=parse_datetime(last_refresh)):

		posts.append({
		'id':post.id,
		'post_input_text':post.post_input_text,
		'date_created':post.date_created,
		'user':post.user.id,
		'first_name':post.user.first_name,
		'last_name':post.user.last_name,
			})
	comments=[]
	for comment in Comment.objects.filter(date_created__gte=parse_datetime(last_refresh)):

		comments.append({
		'id':comment.id,
		'comment_input_text':comment.comment_input_text,
		'date_created':comment.date_created,
		'first_name':comment.user.first_name,
		'last_name':comment.user.last_name,
		'postid':comment.post.id,
		'user':comment.user.id,
		})

	response_text =json.dumps({'posts':posts,'comments':comments},cls=DjangoJSONEncoder)
	return HttpResponse(response_text, content_type='application/json')

@login_required

def loadGlobalStream(request):
	if request.method=="GET":
			last_refresh="1970-01-01T00:00:01.988Z"
	elif request.method=='POST':
			last_refresh=request.POST['last_refresh']
	else:
		raise Http404
	posts=[]
		# posts = Post.objects.filter(date_created=parse_datetime(request.GET['last_refresh'])).reverse()
		# comments=Comment.objects.filter(date_created=parse_datetime(request.GET['last_refresh'])).reverse()
	for post in Post.objects.all():

		posts.append({
		'id':post.id,
		'post_input_text':post.post_input_text,
		'date_created':post.date_created,
		'user':post.user.id,
		'first_name':post.user.first_name,
		'last_name':post.user.last_name,
		})
	comments=[]
	for comment in Comment.objects.all():

		comments.append({
		'id':comment.id,
		'comment_input_text':comment.comment_input_text,
		'date_created':comment.date_created,
		'first_name':comment.user.first_name,
		'last_name':comment.user.last_name,
		'postid':comment.post.id,
		'user':comment.user.id,
		})

	response_text =json.dumps({'posts':posts,'comments':comments},cls=DjangoJSONEncoder)
	return HttpResponse(response_text, content_type='application/json')

@login_required

def loadFollowerStream(request):
	print('pigggggg')
	if request.method=="GET":
		last_refresh="1970-01-01T00:00:01.988Z"
	elif request.method=='POST':
		last_refresh=request.POST['last_refresh']
	else:
		raise Http404
	posts_back=[]
	posts = Post.objects.all()
	followings= Profile.objects.get(user = request.user).following.all()
	# filter(date_created=parse_datetime(request.GET['last_refresh'])).reverse()
	comments=Comment.objects.all()
	#filter(date_created=parse_datetime(request.GET['last_refresh'])).reverse()
	for post in Post.objects.filter(user__in=followings):
		posts_back.append({
		'id':post.id,
		'post_input_text':post.post_input_text,
		'date_created':post.date_created,
		'user':post.user.id,
		'first_name':post.user.first_name,
		'last_name':post.user.last_name,
		})
	comments=[]
	for comment in Comment.objects.filter(user__in=followings):

		comments.append({
		'id':comment.id,
		'comment_input_text':comment.comment_input_text,
		'date_created':comment.date_created,
		'first_name':comment.user.first_name,
		'last_name':comment.user.last_name,
		'postid':comment.post.id,
		'user':comment.user.id,
		})

	response_text =json.dumps({'posts':posts_back,'comments':comments},cls=DjangoJSONEncoder)
	return HttpResponse(response_text, content_type='application/json')



@login_required

def refresh_follower(request):
	if request.method=="GET":
		last_refresh="1970-01-01T00:00:01.988Z"
	elif request.method=='POST':
		last_refresh=request.POST['last_refresh']
	else:
		raise Http404
	posts=[]
		 # students = serializers.serialize("json", Student.objects.all())
	followings= Profile.objects.get(user = request.user).following.all()
		# print(followings)
	mother_post = Post.objects.filter(user__in=followings)
		# print(mother_post)
		# comments=Comment.objects.filter(post__in=posts,date_created=parse_datetime(request.GET['last_refresh'])).reverse()
		# for post in Post.objects.filter(user__in=followings,date_created__gte=parse_datetime(last_refresh)):
	for post in mother_post.filter(date_created__gte=parse_datetime(last_refresh)):
		 posts.append({
		'id':post.id,
		'user':post.user.id,
		'post_input_text':post.post_input_text,
		'date_created':post.date_created,
		'first_name':post.user.first_name,
		'last_name':post.user.last_name,
		})
	comments=[]

		# for comment in Comment.objects.filter(post__in=mother_post,date_created__gte=parse_datetime(last_refresh)):
	for comment in Comment.objects.filter(post__in=mother_post,date_created__gte=parse_datetime(last_refresh)):

		comments.append({
		'id':comment.id,
		'comment_input_text':comment.comment_input_text,
		'date_created':comment.date_created,
		'first_name':comment.user.first_name,
		'last_name':comment.user.last_name,
		'postid':comment.post.id,
		'user':comment.user.id
		})

	response_text =json.dumps({'posts':posts,'comments':comments},cls=DjangoJSONEncoder)
	print(response_text)
	return HttpResponse(response_text, content_type='application/json')
