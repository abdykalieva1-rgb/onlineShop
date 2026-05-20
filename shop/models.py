from django.db import models
from django.contrib.auth.models import User
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def __str__(self):
        return self.name
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    price = models.IntegerField()  # Цена в сомах
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    sizes = models.CharField(max_length=50, default="40,41,42",
                             help_text="Указывайте через запятую, например: 40,41,42")
    color = models.CharField(max_length=30, default="white", help_text="Например: white, black, blue, red")
    is_popular = models.BooleanField(default=False, verbose_name="Популярный товар")
    def __str__(self):
        return self.name
class Order(models.Model):
    STATUS_CHOICES = [
        ('New', 'Новый'),
        ('In_Progress', 'В обработке'),
        ('Delivered', 'Доставлен'),
        ('Cancelled', 'Отменен'),
    ]
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_orders',
                                verbose_name="Менеджер")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_orders',
                             verbose_name="Клиент")
    full_name = models.CharField(max_length=255, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    city = models.CharField(max_length=100, default="Бишкек", verbose_name="Город")
    address = models.CharField(max_length=255, verbose_name="Адрес доставки")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New', verbose_name="Статус заказа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                       verbose_name="Итоговая сумма (сом)")
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
    def __str__(self):
        return f"Заказ #{self.id} — {self.full_name}"
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена на момент покупки")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def get_cost(self):
        return self.price * self.quantity
from django.db import models
from django.contrib.auth.models import User
class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'В обработке'),
        ('DELIVERED', 'Доставлен'),
        ('CANCELED', 'Отменен'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    name = models.CharField(max_length=100)
    manager_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон менеджера")
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Заказ #{self.id} — {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE) # Если модель Product в этом же файле
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, default='42')

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"





class ManagerProfile(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('admin', 'Управляющий'),
        ('support', 'Сотрудник Call-центра'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='manager', verbose_name="Роль")
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Оклад")
    bonus_percent = models.FloatField(default=0.0, verbose_name="Процент бонуса (%)")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер WhatsApp")
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

