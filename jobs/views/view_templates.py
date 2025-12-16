from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..models import JobTemplate
from ..forms import JobEntryForm, JobTemplateForm

def job_templates(request):
    """Manage job templates"""
    templates = JobTemplate.objects.filter(user=request.user).select_related('user')
    
    if request.method == 'POST':
        form = JobTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.user = request.user
            template.save()
            messages.success(request, _('Template saved successfully!'))
            return redirect('jobs:job_templates')
    else:
        form = JobTemplateForm()
    
    context = {
        'templates': templates,
        'form': form,
    }
    return render(request, 'jobs/templates.html', context)


@login_required

def create_from_template(request, template_id):
    """Create job entry from template"""
    template = get_object_or_404(JobTemplate, id=template_id, user=request.user)
    
    if request.method == 'POST':
        form = JobEntryForm(request.POST, user=request.user)
        if form.is_valid():
            job_entry = form.save()
            messages.success(request, _('Job entry created from template!'))
            return redirect('jobs:job_detail', job_id=job_entry.id)
    else:
        # Pre-fill form with template data
        initial_data = {
            'job_title': template.job_title,
            'employer': template.employer,
            'description': template.description,
        }
        form = JobEntryForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'template': template,
    }
    return render(request, 'jobs/create_job.html', context)


@login_required

def edit_template(request, template_id):
    """Edit job template"""
    template = get_object_or_404(JobTemplate, id=template_id, user=request.user)
    
    if request.method == 'POST':
        form = JobTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, _('Template updated successfully!'))
            return redirect('jobs:job_templates')
    else:
        form = JobTemplateForm(instance=template)
    
    context = {
        'form': form,
        'template': template,
    }
    return render(request, 'jobs/edit_template.html', context)


@login_required

def delete_template(request, template_id):
    """Delete job template"""
    template = get_object_or_404(JobTemplate, id=template_id, user=request.user)
    
    if request.method == 'POST':
        template.delete()
        messages.success(request, _('Template deleted successfully!'))
        return redirect('jobs:job_templates')
    
    return redirect('jobs:job_templates')

