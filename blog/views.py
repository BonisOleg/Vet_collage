from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django.db.models import Q
from .models import Article, BlogCategory


def _user_has_membership(user):
    return (
        user.is_authenticated
        and hasattr(user, 'membership')
        and getattr(user.membership, 'is_active', False)
    )


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
        base = Article.objects.filter(is_published=True).order_by('-published_at')
        articles_owners = list(base.filter(
            Q(category__isnull=True) | Q(category__audience__in=['owners', 'all'])
        )[:4])
        placeholder = {
            'title': 'Про правильне харчування',
            'excerpt': 'Стаття для тих, хто хоче дізнатись більше про здорове харчування для своїх тварин.',
            'slug': None,
            'published_at': None,
        }
        owners_cards = list(articles_owners)
        while len(owners_cards) < 4:
            owners_cards.append(placeholder)
        ctx['articles_owners'] = articles_owners
        ctx['owners_cards'] = owners_cards
        articles_vets = list(base.filter(
            Q(category__isnull=True) | Q(category__audience__in=['vets', 'all'])
        )[:4])
        vets_placeholder = {
            'title': 'Про правильне харчування',
            'excerpt': 'Стаття для тих, хто хоче дізнатись більше про здорове харчування для своїх тварин.',
            'slug': None,
            'published_at': None,
        }
        vets_cards = list(articles_vets)
        while len(vets_cards) < 4:
            vets_cards.append(vets_placeholder)
        ctx['articles_vets'] = articles_vets
        ctx['vets_cards'] = vets_cards
        ctx['user_has_membership'] = _user_has_membership(self.request.user)
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
