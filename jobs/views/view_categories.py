from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..models import Category
from ..forms import CategoryForm

def categories_list(request):
    """List all categories"""
    from django.core.cache import cache
    categories = cache.get('all_categories')
    if categories is None:
        categories = list(Category.objects.only('id', 'name', 'color').order_by('name'))
        cache.set('all_categories', categories, 3600)
    return render(request, 'jobs/categories.html', {'categories': categories})


@login_required

def create_category(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            # Invalidate cache
            from django.core.cache import cache
            cache.delete('all_categories')
            messages.success(request, _('Category created successfully!'))
            return redirect('jobs:categories_list')
    else:
        form = CategoryForm()
    return render(request, 'jobs/category_form.html', {'form': form, 'title': _('Create Category')})


@login_required

def edit_category(request, category_id):
    """Edit an existing category"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            # Invalidate cache
            from django.core.cache import cache
            cache.delete('all_categories')
            messages.success(request, _('Category updated successfully!'))
            return redirect('jobs:categories_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'jobs/category_form.html', {'form': form, 'category': category, 'title': _('Edit Category')})


@login_required

def delete_category(request, category_id):
    """Delete a category"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        # Invalidate cache
        from django.core.cache import cache
        cache.delete('all_categories')
        messages.success(request, _('Category "%(name)s" deleted successfully!') % {'name': category_name})
        return redirect('jobs:categories_list')
    return render(request, 'jobs/delete_category.html', {'category': category})

