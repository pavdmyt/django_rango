from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserProfileForm
from rango.faroo_search import run_query, API_KEY
from rango.serializers import CatSerializer, PageSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view


def index(request):
    context_dict = {}

    # Query the database for a list of ALL categories currently stored.
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list

    # Query the DB for a list of pages currently stored
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
        query = request.POST.get('query', '').strip()

        if query:
            result_list = run_query(query, API_KEY)

        context_dict['result_list'] = result_list

    try:
        # Can we find a category name slug with the given name?
        # If we can't the `get` method raises a `DoesNotExist exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category).order_by('-views')

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
        # don't do anything - the template displays the 'no category' msg.
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
            print(form.errors)  # pragma: no cover
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
                page.first_visit = timezone.now()
                page.save()
                # Redirect to appropriate category page.
                return category(request, category_name_slug)
        else:
            print(form.errors)  # pragma: no cover
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
            try:
                page = Page.objects.get(id=page_id)
            except Page.DoesNotExist:
                page = None

            if page:
                page.views += 1
                page.last_visit = timezone.now()
                page.save()
                # Redirect user to specified URL.
                return HttpResponseRedirect(page.url)

        return HttpResponseRedirect('/rango/')


@login_required
def like_category(request):
    if request.method == 'GET':
        cat_id = request.GET.get('category_id')

        if cat_id:
            cat = Category.objects.get(id=cat_id)
            if cat:
                cat.likes += 1
                cat.save()
                return HttpResponse(cat.likes)


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
            print(form.errors)  # pragma: no cover
    else:
        form = UserProfileForm()

    return render(request, 'rango/profile_registration.html', {'form': form})


def suggest_category(request):
    cat_list = []

    if request.method == 'GET':
        starts_with = request.GET.get('suggestion')

    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/cats.html', {'cats': cat_list})


@login_required
def auto_add_page(request):
    context = {}

    if request.method == 'GET':
        title = request.GET.get('title_data')
        url = request.GET.get('url_data')
        cat_id = request.GET.get('catid_data')

        # Get category.
        try:
            cat = Category.objects.get(id=cat_id)
        except Category.DoesNotExist:
            cat = None

        # Add page to category.
        if title and url and cat_id:
            if cat:
                p = Page.objects.get_or_create(category=cat, title=title)[0]
                p.url = url
                p.save()

                # Fill the context.
                pages = Page.objects.filter(category=cat).order_by('-views')
                context['pages'] = pages

    return render(request, 'rango/page_list.html', context)


class CategoriesViewSet(generics.ListAPIView):
    """
    API endpoint that allows categories to be viewed.
    """
    queryset = Category.objects.all()
    serializer_class = CatSerializer


@api_view(['GET'])
def category_details(request, cat_id):
    """
    API endpoint that allows to view specified category.
    """
    try:
        cat = Category.objects.get(id=cat_id)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CatSerializer(cat)
        return Response(serializer.data)


class PagesViewSet(generics.ListAPIView):
    """
    API endpoint that allows pages to be viewed.
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer


@api_view(['GET'])
def page_details(request, page_id):
    """
    API endpoint that allows to view specified page.
    """
    try:
        page = Page.objects.get(id=page_id)
    except Page.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PageSerializer(page)
        return Response(serializer.data)


#######################################################################
# Helper functions.

def get_category_list(max_results=0, starts_with=None):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    return cat_list
