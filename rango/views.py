from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm


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

    # render the response
    return render(request, 'rango/index.html', context_dict)


def about(request):
    return render(request, 'rango/about.html')


def category(request, category_name_slug):
    context_dict = {}

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


def register(request):

    # Telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when
    # registration succeeds.
    registered = False

    if request.method == 'POST':
        # Grab info from the raw form information.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Save user's form data to the database.
            user = user_form.save()

            # Hash the password with the `set_password` method.
            # Once hashed, user object can be updated.
            user.set_password(user.password)
            user.save()

            # Sort out the UserProfile instance.
            # commit=False since we need to set the user attribute
            # manually. This delays saving the model until we're ready
            # to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Check whether user provide a profile picture.
            # If so, get it from the input form and put it in the
            # UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now save the UserProfile model instance.
            profile.save()

            # Registration was successful.
            registered = True

        # Invalid form or forms.
        # Print problems to the terminal.
        else:
            print(user_form.errors, profile_form.errors)

    # Not HTTP POST.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/pass
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the
                # user in. Send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. We can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    # The request is not HTTP POST.
    else:
        return render(request, 'rango/login.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')
