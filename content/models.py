from django.db import models
from authentication.models import User
from booking.models import Appointment

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    featured_image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    categories = models.CharField(max_length=200, blank=True)  # Store as comma-separated values
    tags = models.CharField(max_length=200, blank=True)  # Store as comma-separated values
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_categories(self, categories):
        self.categories = ','.join(categories)

    def get_categories(self):
        return self.categories.split(',') if self.categories else []

    def set_tags(self, tags):
        self.tags = ','.join(tags)

    def get_tags(self):
        return self.tags.split(',') if self.tags else []

class StaticPage(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# content/models.py

class Review(models.Model):
    salon = models.ForeignKey('api.Salon', on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.salon.name}"

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()