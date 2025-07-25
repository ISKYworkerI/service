from django.db import models
from .utils.image_utils import compress_image
from django.urls import reverse

class Capacity(models.Model):
    """Модель ёмкости"""
    volume = models.CharField(max_length=20, unique=True, verbose_name='Объем')

    def __str__(self):
        return self.volume
    
class OlfactoryNoteCategory(models.Model):
    """Категория ольфакторной ноты(например, верхняя, средняя, базовая)"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название ноты')

    def __str__(self):
        return self.name
    

class OlfactoryNote(models.Model):
    """Ольфакторная нота(например, цитрус, цветы)"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название ноты')
    category = models.ForeignKey(OlfactoryNoteCategory, on_delete=models.CASCADE,
                                 related_name='notes', verbose_name='Категория ноты')
    
    def __str__(self):
        return self.name
    

class OlfactoryFamily(models.Model):
    """Модель ольфакторной семьи"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название ольфакторной семьи')
    description = models.TextField(blank=True, verbose_name='Описание ольфакторной семьи')

    def __str__(self):
        return self.name 
    

class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название ингредиента')
    olfactory_family = models.ForeignKey(OlfactoryFamily, on_delete=models.CASCADE,
                                         related_name='ingredients', verbose_name='Ольфакторная семья')
    show_in_fragrance = models.BooleanField(default=False, verbose_name='Показывать в парфюме')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Category(models.Model):
    """Модель категории"""
    name = models.CharField(max_length=255, unique=True, verbose_name='Название категории')
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                                related_name='subcategories', null=True, blank=True)
    show_in_filters = models.BooleanField(default=True, verbose_name='Показывать в фильтрах')
    show_in_fragrance = models.BooleanField(default=True, verbose_name='Показывать в парфюме')
    filter_name = models.CharField(max_length=50, blank=True, verbose_name='Название фильтра')
    filter_slug = models.SlugField(max_length=50, blank=True, verbose_name='Слаг фильтра')
    description = models.TextField(blank=True, verbose_name='Описание категории')

    def __str__(self):
        if self.parent:
            return f"{self.name} ({self.parent.name})"
        return self.name
    
    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    

class Perfume(models.Model):
    """Модель парфюма"""
    name = models.CharField(max_length=255, verbose_name='Название парфюма')
    slug = models.SlugField(max_length=255, unique=True)
    available = models.BooleanField(default=True)
    capacities = models.ManyToManyField(Capacity, through='PerfumeCapacity',
                                        related_name='perfumes', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='perfumes')
    olfactory_family = models.ForeignKey(OlfactoryFamily, on_delete=models.SET_NULL,
                                         related_name='perfumes', null=True, blank=True)
    top_notes = models.ManyToManyField(OlfactoryFamily, related_name='top_notes',
                                       limit_choices_to={'category__name' : 'Top'}, blank=True)
    middle_notes = models.ManyToManyField(OlfactoryFamily, related_name='middle_notes',
                                          limit_choices_to={'category__name' : 'Middle'}, blank=True)
    base_notes = models.ManyToManyField(OlfactoryFamily, related_name='base_notes',
                                        limit_choices_to={'category__name' : 'Base'}, blank=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    detail_media = models.FileField(upload_to='products/media/%Y/%m/%d', blank=True,
                                    help_text='Дополнительные медиафайлы для парфюма')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Скидка')
    description = models.TextField(blank=True, verbose_name='Описание')
    story = models.TextField(blank=True, verbose_name='История создания парфюма')
    order = models.PositiveIntegerField(default=0)
    show_on_hero = models.BooleanField(default=False, verbose_name='Показывать на главной странице')
    show_in_featured = models.BooleanField(default=False, verbose_name='Показывать в разделе "Избранное"')
    show_in_best_sellers = models.BooleanField(default=False, verbose_name='Показывать в разделе "Бестселлеры"')

    def __str__(self):
        return self.name
    
    def get_price_with_discount(self):
        """Возвращает цену с учетом скидки"""
        if self.discount > 0:
           return round(self.price * (1 - (self.discount / 100)), 2)
        return round(self.price, 2)
    
    def get_absolute_url(self):
        """Возвращает абсолютный URL для парфюма"""
        return reverse('main:perfume_detail', args=[self.slug])


class PerfumeCapacity(models.Model):
    """Доступные ёмкости для парфюма"""
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE, related_name='perfumes_capacities')
    capacity = models.ForeignKey(Capacity, on_delete=models.CASCADE, related_name='perfumes_capacities')
    available = models.BooleanField(default=True, verbose_name='Доступно')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True ,verbose_name='Цена')

    class Meta:
        unique_together = ('perfume', 'capacity')
        verbose_name = 'Ёмкость парфюма'
        verbose_name_plural = 'Ёмкости парфюмов'

    def __str__(self):
        return f'{self.perfume.name} - {self.capacity.volume}'
        
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.perfume.price
        super().save(*args, **kwargs)


class PerfumeImage(models.Model):
    """Модель изображения парфюма"""
    product = models.ForeignKey(Perfume, on_delete=models.CASCADE, related_name='images', verbose_name='Парфюм')
    image = models.ImageField(upload_to='products/%Y/%m/%d',blank=True, verbose_name='Изображение парфюма')

    def __str__(self):
        return f'{self.product.name} - {self.image.name}'
    
    def save(self, *args, **kwargs):
        if self.image.size > 5 * 1024 * 1024:  # Ограничение размера изображения до 5 МБ
            self.image = compress_image(self.image)
        super().save(*args, **kwargs)
