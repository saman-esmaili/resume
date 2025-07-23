from django.db.models import Q
from django.views.generic import ListView
from django.core.cache import cache
from auths.forms.form import SearchMealForm
from auths.models import Meal
from django.dispatch import receiver
from django.db.models.signals import post_save
class MealView(ListView):
    template_name = 'auth/menu.html'
    form_class = SearchMealForm
    context_object_name = 'meals'
    paginate_by = 12
    model = Meal
    def get_queryset(self):
        queryset = Meal.objects.order_by('id')
        form = SearchMealForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('searchInput')
            if query:
                if cache.get(f"meal-search:{query}"):
                    queryset = cache.get(f"meal-search:{query}")
                else:
                    queryset = queryset.filter(Q(name__icontains=query) |
                                               Q(category__icontains=query)).order_by('id')
                    cache.set(f"meal-search:{query}",queryset,timeout=300)
        return queryset

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchMealForm(self.request.GET)
        return context


@receiver(post_save,sender=Meal)
def clear_cache(sender,instance,**kwargs):
    cache.clear()