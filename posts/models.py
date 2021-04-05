from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.text import slugify
import pytils


# Create your models here.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Post(models.Model):
    objects = models.Manager()
    published = PublishedManager()
    Status_Post = (
        ('draft', 'Черновик'),
        ('published', 'Опубликована')
    )

    title = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=100, blank=True)
    author = models.ForeignKey(User, related_name='blog_post', on_delete=models.CASCADE)
    body = models.TextField(verbose_name='Текст статьи')
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=Status_Post, verbose_name='Статус статьи')
    views = models.IntegerField(default=0, verbose_name='Просмотры')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.id, self.slug])

    def total_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ['-id']


@receiver(pre_save, sender=Post)
def pee_save_plug(sender, **kwargs):
    slug = pytils.translit.slugify(kwargs['instance'].title)
    kwargs['instance'].slug = slug


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    photo = models.ImageField(null=True, blank=True, verbose_name='Фотография профиля')

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.ForeignKey('self', null=True, related_name='replies', on_delete=models.CASCADE)
    content = models.CharField(max_length=200, verbose_name='Текст коментария')
    time_of_comment = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.post.title} - {self.user.username}'

