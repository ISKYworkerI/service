from .models import Category, OlfactoryFamily, Ingredient, Perfume
from django.shortcuts import render
from django.db.models import Q
from django.core.cache import cache

def fragrance_menu(request):
    return {
        'fragrance_categories': Category.objects.filter(show_in_fragrance=True),
        'olfactory_families': OlfactoryFamily.objects.all(),
        'fragrance_ingredient': Ingredient.objects.filter(show_in_fragrance=True),
    }

def navigation_categories(request):
    cahce_key = 'navigation_categories'
    categories = cache.get(cahce_key)
    if not categories:
        categories = Category.objects.all()[:3]
        cache.set(cahce_key, categories, 60 * 60)
    return {'navigation_categories' : categories}

def search_results(request):
    query = request.GET.get('q', '').strip()
    context = {
        'query': query,
        'results': [],
        'categories': [],
        'olfactory_families': [],
        'ingredients': [],
    }

    if query:
        # Поиск по парфюму
        context['result'] = Perfume.objects.filter(
            Q(name__icontains=query) & Q(available=True)
        ).distinct()[:10]

        # Поиск по категориям
        context['categories'] = Perfume.objects.filter(
            Q(name__icontains=query) & Q(show_in_frarances=True)
        )[:5]

        # Поиск по ольфакторной семье
        context['olfactory_families'] = Perfume.objects.filter(
            Q(name__icontains=query)
        )[:5]

        # Поиск по ингредиентам
        context['ingredients'] = Perfume.objects.filter(
            Q(name__icontains=query) & Q(show_in_frarances=True)
        )
    return render(request, 'search/results.html', context)