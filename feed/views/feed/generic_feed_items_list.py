from django.views.generic import ListView
from django.utils.translation import gettext_noop as _

from feed.models import FeedItem
from feed.views.mixins import PageMetaMixin


class GenericFeedItemListView(ListView, PageMetaMixin):
    model = FeedItem
    paginate_by = 20
    applied_filters = {'only_interesting': True}
    title = _('Feed')

    def setup(self, request, *args, **kwargs):
        filters = self.init_filters(request)
        if filters:
            new_filters = dict()
            for name in filters:
                new_filters[name] = True
            self.applied_filters = new_filters

        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        only_interesting = self.applied_filters.get('only_interesting', False)
        if only_interesting:
            return self.model.objects.exclude(usersettings__user=self.request.user)

        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context['page_obj']

        if hasattr(self.request.user, 'usersettings'):
            context['hidden_feed_items'] = self.request.user.usersettings.hidden_feed_items.all()
        context['paginator_range'] = page.paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
        context['applied_filters'] = self.applied_filters
        context['applied_filters_str'] = self.applied_filters_str
        return context

    def init_filters(self, request):
        request_params = request.GET if request.method == 'GET' else request.POST
        return request_params.getlist('filter')

    @property
    def applied_filters_str(self):
        return '&'.join([f'filter={k}' for k, v in self.applied_filters.items() if v])
