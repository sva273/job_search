from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..models import Attachment, JobEntry
from ..forms import AttachmentForm

def upload_attachment(request, job_id):
    """Upload attachment to job entry"""
    job_entry = get_object_or_404(JobEntry, id=job_id, user=request.user)
    
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.job_entry = job_entry
            attachment.file_name = request.FILES['file'].name
            attachment.file_type = request.FILES['file'].content_type
            attachment.save()
            messages.success(request, _('File uploaded successfully!'))
            return redirect('jobs:job_detail', job_id=job_id)
    else:
        form = AttachmentForm()
    
    context = {
        'form': form,
        'job_entry': job_entry,
    }
    return render(request, 'jobs/upload_attachment.html', context)


@login_required

def delete_attachment(request, attachment_id):
    """Delete attachment"""
    attachment = get_object_or_404(Attachment, id=attachment_id, job_entry__user=request.user)
    job_id = attachment.job_entry.id
    attachment.delete()
    messages.success(request, _('Attachment deleted!'))
    return redirect('jobs:job_detail', job_id=job_id)

