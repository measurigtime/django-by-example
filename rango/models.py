from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title


class Like(models.Model):
    category_id= models.ForeignKey(Category)
    user_id= models.ForeignKey(User)
    liked= models.IntegerField(default=0)
    category_likes = models.IntegerField(default = 0)


class UserProfile(models.Model):
    # This line is required. Links a user profile to a user model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    website = models.URLField(blank = True)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    pages_liked = models.ManyToManyField(Page, related_name='users_who_like')
    categories_liked = models.ManyToManyField(Category, related_name="users_who_like", through="Like")

    # Override the __unicode__ method to return something meaningful
    def __unicode__(self):
        return self.user.username
