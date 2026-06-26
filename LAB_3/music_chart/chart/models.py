from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Track(models.Model):
    artist = models.CharField('Исполнитель', max_length=200)
    artist_info = models.TextField('Информация об Исполнителе')
    title = models.CharField('Название трека', max_length=200)
    genre = models.CharField('Жанр', max_length=100)
    release_year = models.IntegerField('Год выпуска')
    lyrics = models.TextField('Текст песни')
    cover = models.ImageField('Обложка/Фото', upload_to='covers/', blank=True, null=True)
    
    def get_rating(self):
        avg = self.votes.aggregate(Avg('score'))['score__avg']
        return round(avg, 1) if avg else 0.0

    def get_votes_count(self):
        return self.votes.count()

    def __str__(self):
        return f"{self.artist} - {self.title}"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, related_name='votes', on_delete=models.CASCADE)
    score = models.IntegerField('Оценка', validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        unique_together = ('user', 'track')
