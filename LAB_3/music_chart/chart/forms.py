from django import forms
from .models import Track


class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['artist', 'artist_info', 'title', 'genre', 'release_year', 'lyrics', 'cover']
