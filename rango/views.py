from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.faroo_search import run_query, API_KEY


def index(request):
    context_dict = {}

    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our `context_dict` which will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list

    # Query the DB for a list of pages currently stored
    # Order the pages by no. of views, retrieve the top 5
    pages_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = pages_list

    #
    # Cookies to calculate number of site visits.
    #
    visits = request.session.get('visits', 1)
    reset_last_visit_time = False

    # Does the cookie `last_visit` exist?
    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7],
                                            "%Y-%m-%d %H:%M:%S")

        # If it's been more than a day since the last visit...
        if (datetime.now() - last_visit_time).days > 0:
            visits += 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits

    context_dict['visits'] = visits

    return render(request, 'rango/index.html', context_dict)


def about(request):
    return render(request, 'rango/about.html')


def category(request, category_name_slug):
    context_dict = {}

    # For searching.
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query, API_KEY)

        context_dict['result_list'] = result_list
        # return render(request, 'rango/search.html', context_dict)

    try:
        # Can we find a category name slug with the given name?
        # If we can't the `get` method raises a `DoesNotExist exception.
        # So the `get` method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)

        # Add results list to the template context under name pages
        context_dict['pages'] = pages

        # Add the category object from the database to the context dict.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category

        # Provide appropriate link to the add page capability
        # /rango/category/<category_name_url>/add_page/
        context_dict['cat_name_slug'] = category_name_slug

    except Category.DoesNotExist:
        # we get here if we didn't find the specified category.
        # don't do anything - the template displays the 'no category' msg for us
        pass

    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)

            # Now call the index() view
            # The user will be shown the homepage
            return index(request)
        else:
            # The supplied form contained errors - just print the to the terminal
            print(form.errors)
    else:
        # If the request was not a POST, display the form to enter details
        form = CategoryForm()

    # Bad form (of form details), no form supplied...
    # Render the form wit error messages (if any)
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # Redirect to appropriate category page.
                return category(request, category_name_slug)
        else:
            print(form.errors)
    else:
        form = PageForm()

    context_dict = {'form': form,
                    'category': cat,
                    'cat_name_slug': category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)


@login_required
def user_settings(request):
    context = {}

    try:
        profile = UserProfile.objects.get(user=request.user._wrapped)
    except UserProfile.DoesNotExist:
        pass
    else:
        context['profile'] = profile

    return render(request, 'registration/user_settings.html', context)


def track_url(request):
    if request.method == 'GET':
        page_id = request.GET.get('page_id')

        if page_id:
            # Fetch the page by ID and increment views field.
            page = Page.objects.filter(id=page_id)[0]
            page.views += 1
            page.save()

            # Redirect user to specified URL.
            return HttpResponseRedirect(page.url)
        else:
            return HttpResponseRedirect('/rango/')


@login_required
def register_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user._wrapped
            profile.save()
            return HttpResponseRedirect('/rango/')
        else:
            print(form.errors)
    else:
        form = UserProfileForm()

    return render(request, 'rango/profile_registration.html', {'form': form})
