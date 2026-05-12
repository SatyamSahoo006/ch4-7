from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from actions.utils import create_action
from .forms import ImageCreateForm
from .models import Image

try:
    import redis
    from django.conf import settings
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
except Exception:
    r = None


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image added successfully')
            return redirect(new_image.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images', 'form': form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = None
    if r:
        try:
            total_views = r.incr(f'image:{image.id}:views')
            r.zincrby('image_ranking', 1, image.id)
        except Exception:
            pass
    return render(request, 'images/image/detail.html', {
        'section': 'images',
        'image': image,
        'total_views': total_views,
    })


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page', 1)
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    template = 'images/image/list_ajax.html' if images_only else 'images/image/list.html'
    return render(request, template, {'section': 'images', 'images': images})


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            image.total_likes = image.users_like.count()
            image.save()
            return JsonResponse({'status': 'ok', 'total_likes': image.total_likes})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_ranking(request):
    if not r:
        return render(request, 'images/image/ranking.html', {'section': 'images', 'most_viewed': []})
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ids = [int(id) for id in image_ranking]
    most_viewed = list(Image.objects.filter(id__in=image_ids))
    most_viewed.sort(key=lambda x: image_ids.index(x.id))
    return render(request, 'images/image/ranking.html', {
        'section': 'images',
        'most_viewed': most_viewed,
    })
