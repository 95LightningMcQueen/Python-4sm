from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import Track, Vote
from .forms import TrackForm


def is_admin(user):
    return user.is_authenticated and user.is_superuser

def index(request):
    tracks_list = Track.objects.all().order_by('-id')
    paginator = Paginator(tracks_list, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for track in page_obj:
            data.append({
                'id': track.id,
                'artist': track.artist,
                'title': track.title,
                'genre': track.genre,
                'release_year': track.release_year,
                'rating': track.get_rating(),
                'votes_count': track.get_votes_count(),
                'cover_url': track.cover.url if track.cover else '',
            })
        return JsonResponse({'tracks': data, 'has_next': page_obj.has_next()})
    return render(request, 'chart/index.html')

def track_detail(request, pk):
    track = get_object_or_404(Track, pk=pk)
    user_voted = False
    if request.user.is_authenticated:
        vote = Vote.objects.filter(user=request.user, track=track).first()
        if vote is not None:
            user_voted = True
    
    return render(request, 'chart/track_detail.html', {'track': track, 'user_voted': user_voted})

@user_passes_test(is_admin)
def add_track(request):
    if request.method == 'POST':
        form = TrackForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TrackForm()
    return render(request, 'chart/add_track.html', {'form': form})

@login_required
def vote(request, pk):
    if request.method == 'POST':
        score = int(request.POST.get('score', 0))
        if 1 <= score <= 10:
            track = get_object_or_404(Track, pk=pk)
            vote_obj, created = Vote.objects.get_or_create(
                user=request.user, 
                track=track,
                defaults={'score': score}
            )
            if created:
                return JsonResponse({'status': 'success', 'new_rating': track.get_rating(), 'votes': track.get_votes_count()})
            else:
                return JsonResponse({'status': 'error', 'message': 'Вы уже голосовали.'})
    return JsonResponse({'status': 'error'})
