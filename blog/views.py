from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Article, BlogCategory


def _user_has_membership(user) -> bool:
    if not user.is_authenticated:
        return False
    try:
        return hasattr(user, 'membership') and user.membership.is_active
    except Exception:
        return False


class ArticleListView(ListView):
    model = Article
    template_name = 'pages/blog/list_new.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        self._is_member = _user_has_membership(request.user)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = Article.objects.filter(is_published=True).select_related('category')
        if not getattr(self, '_is_member', False):
            qs = qs.filter(requires_membership=False)

        category = self.request.GET.get('category')
        audience = self.request.GET.get('audience')
        q = self.request.GET.get('q', '').strip()

        if category:
            qs = qs.filter(category__slug=category)
        if audience:
            qs = qs.filter(category__audience=audience)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q))

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        is_htmx = self.request.headers.get('HX-Request')

        ctx['categories'] = BlogCategory.objects.all()
        ctx['user_has_membership'] = getattr(self, '_is_member', False)

        if is_htmx:
            self.template_name = 'pages/blog/partials/article_list.html'

        return ctx


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'pages/blog/detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.filter(is_published=True).select_related(
            'category', 'author',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        article = self.object
        has_access = not article.requires_membership or _user_has_membership(user)
        ctx['has_access'] = has_access

        if not has_access and article.content:
            preview_length = min(len(article.content), 500)
            cut = article.content[:preview_length]
            last_space = cut.rfind(' ')
            if last_space > 0:
                cut = cut[:last_space]
            ctx['content_preview'] = cut + '...'
        else:
            ctx['content_preview'] = ''

        ctx['related_articles'] = Article.objects.filter(
            is_published=True,
            category=article.category,
        ).exclude(pk=article.pk)[:3] if article.category else []

        return ctx
