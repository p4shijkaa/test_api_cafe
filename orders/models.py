from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Dish(models.Model):
	CATEGORY_CHOICES = [
		('appetizers', 'Закуски'),
		('main', 'Основные блюда'),
		('desserts', 'Десерты'),
		('drinks', 'Напитки'),
	]

	name = models.CharField('Название', max_length=30)
	description = models.TextField('Описание', blank=True)
	price = models.DecimalField(
		'Цена',
		max_digits=8,
		decimal_places=2,
		validators=[MinValueValidator(0.01)]
	)
	category = models.CharField(
		'Категория',
		max_length=50,
		choices=CATEGORY_CHOICES
	)
	created_at = models.DateTimeField('Дата создания', auto_now_add=True)
	updated_at = models.DateTimeField('Дата обновления', auto_now=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Блюдо'
		verbose_name_plural = 'Блюда'
		ordering = ['category', 'name']


class Order(models.Model):
	STATUS_CHOICES = [
		('pending', 'В обработке'),
		('preparing', 'Готовится'),
		('delivering', 'Доставляется'),
		('completed', 'Завершен'),
		('canceled', 'Отменен'),
	]

	STATUS_TRANSITIONS = {
		'pending': ['preparing', 'canceled'],
		'preparing': ['delivering', 'canceled'],
		'delivering': ['completed'],
		'completed': [],
		'canceled': [],
	}

	customer_name = models.CharField('Имя клиента', max_length=20)
	dishes = models.ManyToManyField(
		Dish,
		related_name='orders',
		verbose_name='Блюда'
	)
	order_time = models.DateTimeField('Время заказа', default=timezone.now)
	status = models.CharField(
		'Статус',
		max_length=20,
		choices=STATUS_CHOICES,
		default='pending'
	)
	total_price = models.DecimalField(
		'Общая стоимость',
		max_digits=10,
		decimal_places=2,
		default=0,
		validators=[MinValueValidator(0)]
	)
	created_at = models.DateTimeField('Дата создания', auto_now_add=True)
	updated_at = models.DateTimeField('Дата обновления', auto_now=True)

	def __str__(self):
		return f"Заказ #{self.id} - {self.customer_name}"

	class Meta:
		verbose_name = 'Заказ'
		verbose_name_plural = 'Заказы'
		ordering = ['-order_time']

	def save(self, *args, **kwargs):
		if not self.pk:
			super().save(self, *args, **kwargs)
		self.total_price = sum(dish.price for dish in self.dishes.all())
		super().save(*args, **kwargs)