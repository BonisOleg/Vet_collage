from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Article, BlogCategory


class ArticleListView(ListView):
    model = Article
    template_name = 'pages/blog/list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        qs = Article.objects.filter(is_published=True)
        category = self.request.GET.get('category')
        audience = self.request.GET.get('audience')
        if category:
            qs = qs.filter(category__slug=category)
        if audience:
            qs = qs.filter(category__audience=audience)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = BlogCategory.objects.all()
        if self.request.headers.get('HX-Request'):
            self.template_name = 'pages/blog/partials/article_list.html'
        return ctx


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'pages/blog/detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        article = self.object
        ctx['has_access'] = (
            not article.requires_membership
            or (user.is_authenticated and hasattr(user, 'membership') and user.membership.is_active)
        )
        return ctx
