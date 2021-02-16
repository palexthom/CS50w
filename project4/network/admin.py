from django.contrib import admin
from .models import Post, User


class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'timestamp')


# Register your models here.
admin.site.register(Post)
admin.site.register(User)
