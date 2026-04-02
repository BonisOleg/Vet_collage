from django.contrib import admin
from .models import Article, BlogCategory


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'audience']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['audience']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'author', 'is_published',
        'requires_membership', 'published_at',
    ]
    list_filter = ['is_published', 'requires_membership', 'category', 'published_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'published_at'
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author', 'cover'),
        }),
        ('Контент', {
            'fields': ('excerpt', 'content'),
        }),
        ('Публікація', {
            'fields': ('is_published', 'published_at', 'requires_membership'),
        }),
    )
