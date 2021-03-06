from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm, LikeForm
from django.contrib.auth.models import User
from rango.models import Category, Page, Like
from datetime import datetime
from django.utils import timezone
from rango.bing_search import run_query


def index(request):
	# Query the database for a list of ALL categories currently stored.
	# Order the categories by no. likes in descending order.
	# Retrieve the top 5 only - or all if less than 5.
	# Place the list in our context_dict dictionary which will be passed to the template engine.
	context_dict ={}
	#full_category_list = Category.objects.all()
	category_list = Category.objects.order_by('-views')[:5]
	context_dict['categories'] = category_list
	page_list = Page.objects.order_by('-views')[:5]
	context_dict['pages'] = page_list
	#context_dict['full_category_list'] = full_category_list
	response = render(request, 'rango/index.html', context_dict)
	'''
	# COOKIE_METHOD
	# Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.
	visits = int(request.COOKIES.get('visits', '1'))

	reset_last_visit_time = False
	response = render(request, 'rango/index.html', context_dict)
	# Does the cookie last_visit exist?
	if 'last_visit' in request.COOKIES:
		 # Yes it does! Get the cookie's value.
 		last_visit = request.COOKIES['last_visit']
 		# Cast the value to a Python date/time object.
 		#last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

 		# If it's been more than a day since the last visit...
		if (datetime.now() - last_visit_time).seconds > 5:
 			visits = visits + 1
            # ...and flag that the cookie last visit needs to be updated
 			reset_last_visit_time = True
	else:
        # Cookie last_visit doesn't exist, so flag that it should be set.
 		reset_last_visit_time = True

		context_dict['visits'] = visits

        #Obtain our Response object early so we can add cookie information.
		response = render(request, 'rango/index.html', context_dict)

	if reset_last_visit_time:
		response.set_cookie('last_visit', datetime.now())
		response.set_cookie('visits', visits)
	'''

	# SESSION_METHOD. All data stored in backend, so safe.
	visits = request.session.get('visits')
	if not visits:
		visits = 1
	reset_last_visit_time = False
	last_visit_time = datetime.now()

	last_visit = request.session.get('last_visit')
	if last_visit:
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		if (datetime.now() - last_visit_time).seconds > 0:
	        # ...reassign the value of the cookie to +1 of what it was before...
			visits = visits + 1
	        # ...and update the last visit cookie, too.
			reset_last_visit_time = True
	else:
	    # Cookie last_visit doesn't exist, so create it to the current date/time.
		reset_last_visit_time = True

	if reset_last_visit_time:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = visits

	context_dict['visits'] = visits
	context_dict['last_visit'] = last_visit_time

	response = render(request,'rango/index.html', context_dict)

	return response


def about(request):
	if request.session.get('visits'):
		count = request.session.get('visits')

	else:
		count = 0
	return render(request, 'rango/about.html', {'visits':count})


def category(request, category_name_slug):
	context_dict = {}
	try:
		if request.method=='POST':
			category = Category.objects.get(slug = category_name_slug)
			category.views += 1
			category.save()
			context_dict['category_name'] = category.name

			pages = Page.objects.filter(category = category)
			context_dict['pages'] = pages

			context_dict['category'] = category
			context_dict['category_name_slug'] = category_name_slug
			user = request.user

			if user:
				if category in user.categories_liked:
					context_dict['liked'] = 1
				else:
					context_dict['liked'] = 0

		if request.method=='POST':
			form = LikeForm(request.POST)

			if form.is_valid():
				user = request.user
				cat = Category.objects.get(slug=category_name_slug)
				page = form.save(commit=False)
				page.category_id= cat.id
				page.user_id = user.id
				page.save()
				page.category_likes = cat.likes + page.liked

				if request.POST['']
					user.categories_liked.add(cat)
					cat.user_set.add(user)
					# cat.save()
					user.save()
				else:
					user.categories_liked.remove(cat)
					cat.user_set.remove(user)
					# cat.save()
					user.save()

				cat.likes = page.category_likes
				cat.save()
				# page.save()
				return category(request, category_name_slug)

			else:
				print form.errors

	except Category.DoesNotExist:
		pass

	return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			cat = form.save(commit=True)
			print cat, cat.slug
			return index(request)

		else:
			print form.errors

	else:
		form = CategoryForm()

	return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
	try:
		cat = Category.objects.get(slug=category_name_slug)

	except Category.DoesNotExist:
		cat = None

	if request.method=='POST':
		form = PageForm(request.POST)

		if form.is_valid():
			if cat:
				page = form.save(commit = False)
				page.category = cat
				page.views = 0
				page.save()
				return category(request, category_name_slug)

		else:
			print form.errors

	else:
		form = PageForm()

	context_dict = {'form': form, 'category': cat, 'category_name_slug': category_name_slug}

	return render(request, 'rango/add_page.html', context_dict)


# def register(request):
# 	registered = False

# 	if request.method=='POST':
# 		user_form = UserForm(data=request.POST)
# 		profile_form = UserProfileForm(data=request.POST)

# 		if user_form.is_valid() and profile_form.is_valid():
# 			user = user_form.save()
# 			user.set_password(user.password)
# 			user.save()

# 			profile = profile_form.save(commit=False)
# 			profile.user = user

# 			if 'picture' in request.FILES:
# 				profile.picture = request.FILES['picture']

# 			profile.save()
# 			registered = True

# 		else:
# 			print user_form.errors, profile_form.errors

# 	else:
# 		user_form = UserForm()
# 		profile_form = UserProfileForm()

# 	return render(request, 'rango/register.html',
# 				{'user_form': user_form, 'profile_form':profile_form, 'registered':registered})


# def user_login(request):

# 	# If the request is a HTTP POST, try to pull out the relevant information.
# 	if request.method == 'POST':
# 		# Gather the username and password provided by the user.
# 		# This information is obtained from the login form.
# 				# We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
# 				# because the request.POST.get('<variable>') returns None, if the value does not exist,
# 				# while the request.POST['<variable>'] will raise key error exception
# 		username = request.POST.get('username')
# 		password = request.POST.get('password')

# 		# Use Django's machinery to attempt to see if the username/password
# 		# combination is valid - a User object is returned if it is.
# 		user = authenticate(username=username, password=password)

# 		# If we have a User object, the details are correct.
# 		# If None (Python's way of representing the absence of a value), no user
# 		# with matching credentials was found.
# 		if user:
# 			# Is the account active? It could have been disabled.
# 			if user.is_active:
# 				# If the account is valid and active, we can log the user in.
# 				# We'll send the user back to the homepage.
# 				login(request, user)
# 				return HttpResponseRedirect('/rango/')
# 			else:
# 				# An inactive account was used - no logging in!
# 				return HttpResponse("Your Rango account is disabled.")
# 		else:
# 			# Bad login details were provided. So we can't log the user in.
# 			print "Invalid login details: {0}, {1}".format(username, password)
# 			login_error = True
# 			return render(request, 'rango/login.html', {'login_error': login_error})

# 	# The request is not a HTTP POST, so display the login form.
# 	# This scenario would most likely be a HTTP GET.
# 	else:
# 		# No context variables to pass to the template system, hence the
# 		# blank dictionary object...
# 		return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
	return HttpResponse("Since you are logged in you can see this.")


# @login_required
# def user_logout(request):
# 	logout(request)
# 	return HttpResponseRedirect('/rango/')

def search(request):
	result_list = []
	context_dict = {}
	if request.method == 'POST':
		query = request.POST['query'].strip()
		context_dict['query'] = query
		if query:
			# Run our bing search on the query to get results
			result_list = run_query(query)
			context_dict['result_list'] = result_list
	return render(request, 'rango/search.html', context_dict)


def track_url(request):
	url = '/rango/'

	if request.method=='GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			page = Page.objects.get(id=page_id)
			page.views += 1
			page.save()
			url = page.url

	return redirect(url)

