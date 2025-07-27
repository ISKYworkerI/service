from django.db import models
from .utils.image_utils import compress_image
from django.urls import reverse


class Capacity(models.Model):
    """Модель для объема флакона (например, 50ml, 100ml)"""
    volume = models.CharField(max_length=20, unique=True, verbose_name="Объем")
    
    def __str__(self):
        return self.volume

    class Meta:
        verbose_name = 'объем'
        verbose_name_plural = 'объемы'


class OlfactoryNoteCategory(models.Model):
    """Категория нот (верхние, средние, базовые)"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Название категории")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категория нот'
        verbose_name_plural = 'категории нот'


class OlfactoryNote(models.Model):
    """Ольфакторная нота (например, бергамот, амбра)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название ноты")
    category = models.ForeignKey(OlfactoryNoteCategory, on_delete=models.CASCADE, 
                               related_name='notes', verbose_name="Категория")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ольфакторная нота'
        verbose_name_plural = 'ольфакторные ноты'


class OlfactoryFamily(models.Model):
    """Ольфакторная семья (например, Amber Oriental)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название семьи")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ольфакторная семья'
        verbose_name_plural = 'ольфакторные семьи'


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название ингредиента")
    olfactory_family = models.ForeignKey(OlfactoryFamily, on_delete=models.CASCADE, 
                                       related_name='ingredients', verbose_name="Ольфакторная семья")
    show_in_fragrances = models.BooleanField(default=False, 
                                           verbose_name="Показывать в выпадающем меню парфюмов")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="Слаг")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='subcategories', verbose_name="Родительская категория")
    show_in_filters = models.BooleanField(default=False, 
                                        verbose_name="Показывать в разделе фильтров")
    show_in_fragrances = models.BooleanField(default=False, 
                                           verbose_name="Показывать в выпадающем меню парфюмов")
    filter_name = models.CharField(max_length=50, blank=True, 
                                 verbose_name="Название фильтра (если отличается от категории)")
    filter_slug = models.SlugField(max_length=50, blank=True, 
                                 verbose_name="Слаг фильтра (для фронтенда)")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        if self.parent:
            return f"{self.name} ({self.parent.name})"
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'категория'
        verbose_name_plural = 'категории'


class Perfume(models.Model):
    """Модель парфюма"""
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="Слаг")
    available = models.BooleanField(default=True, verbose_name="Доступен")
    capacities = models.ManyToManyField(Capacity, through='PerfumeCapacity', 
                                      related_name='perfumes', blank=True, verbose_name="Объемы")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                               related_name='perfumes', verbose_name="Категория")
    olfactory_family = models.ForeignKey(OlfactoryFamily, on_delete=models.SET_NULL, 
                                       null=True, blank=True, related_name='perfumes', 
                                       verbose_name="Ольфакторная семья")
    top_notes = models.ManyToManyField(OlfactoryNote, related_name='top_notes', 
                                     limit_choices_to={'category__name': 'Top'}, blank=True, 
                                     verbose_name="Верхние ноты")
    middle_notes = models.ManyToManyField(OlfactoryNote, related_name='middle_notes', 
                                        limit_choices_to={'category__name': 'Middle'}, blank=True, 
                                        verbose_name="Средние ноты")
    base_notes = models.ManyToManyField(OlfactoryNote, related_name='base_notes', 
                                      limit_choices_to={'category__name': 'Base'}, blank=True, 
                                      verbose_name="Базовые ноты")
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name="Изображение")
    detail_media = models.FileField(upload_to='products/media/%Y/%m/%d', blank=True, 
                                  help_text="Загрузите изображение или видео для страницы деталей", 
                                  verbose_name="Медиа для деталей")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Скидка")
    description = models.TextField(blank=True, verbose_name="Описание")
    story = models.TextField(blank=True, help_text="История создания парфюма", 
                           verbose_name="История")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    show_on_hero = models.BooleanField(default=False, 
                                     verbose_name="Показывать в главной секции (кнопка плюс)")
    show_in_featured = models.BooleanField(default=False, 
                                         verbose_name="Показывать в разделе избранных продуктов")
    show_in_best_sellers = models.BooleanField(default=False, 
                                             verbose_name="Показывать в разделе бестселлеров")

    def __str__(self):
        return self.name

    def get_price_with_discount(self):
        if self.discount > 0:
            return round(self.price * (1 - (self.discount / 100)), 2)
        return round(self.price, 2)

    def get_absolute_url(self):
        return reverse('main:perfume_detail', args=[self.slug])

    class Meta:
        verbose_name = 'парфюм'
        verbose_name_plural = 'парфюмы'


class PerfumeCapacity(models.Model):
    """Доступные объемы для парфюма"""
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE, verbose_name="Парфюм")
    capacity = models.ForeignKey(Capacity, on_delete=models.CASCADE, verbose_name="Объем")
    available = models.BooleanField(default=True, verbose_name="Доступен")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                              verbose_name="Цена")

    class Meta:
        unique_together = ('perfume', 'capacity')
        verbose_name = 'объем парфюма'
        verbose_name_plural = 'объемы парфюмов'

    def __str__(self):
        return f"{self.perfume.name} - {self.capacity.volume}"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.perfume.price
        super().save(*args, **kwargs)


class PerfumeImage(models.Model):
    """Изображения парфюма"""
    product = models.ForeignKey(Perfume, related_name='images', on_delete=models.CASCADE, 
                              verbose_name="Парфюм")
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name="Изображение")
    
    def __str__(self):
        return f'{self.product.name} - {self.image.name}'

    def save(self, *args, **kwargs):
        if self.image.size > 5 * 1024 * 1024:
            self.image = compress_image(self.image)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'изображение парфюма'
        verbose_name_plural = 'изображения парфюмов'