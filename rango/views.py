from django.shortcuts import render
# from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm


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
