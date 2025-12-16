from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..models import Tag
from ..forms import TagForm

def tags_list(request):
    """List all tags"""
    from django.core.cache import cache
    tags = cache.get('all_tags')
    if tags is None:
        tags = list(Tag.objects.only('id', 'name').order_by('name'))
        cache.set('all_tags', tags, 3600)
    return render(request, 'jobs/tags.html', {'tags': tags})


@login_required

def create_tag(request):
    """Create a new tag"""
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Tag created successfully!'))
            return redirect('jobs:tags_list')
    else:
        form = TagForm()
    return render(request, 'jobs/tag_form.html', {'form': form, 'title': _('Create Tag')})


@login_required

def edit_tag(request, tag_id):
    """Edit an existing tag"""
    tag = get_object_or_404(Tag, id=tag_id)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, _('Tag updated successfully!'))
            return redirect('jobs:tags_list')
    else:
        form = TagForm(instance=tag)
    return render(request, 'jobs/tag_form.html', {'form': form, 'tag': tag, 'title': _('Edit Tag')})


@login_required

def delete_tag(request, tag_id):
    """Delete a tag"""
    tag = get_object_or_404(Tag, id=tag_id)
    if request.method == 'POST':
        tag_name = tag.name
        tag.delete()
        messages.success(request, _('Tag "%(name)s" deleted successfully!') % {'name': tag_name})
        return redirect('jobs:tags_list')
    return render(request, 'jobs/delete_tag.html', {'tag': tag})



