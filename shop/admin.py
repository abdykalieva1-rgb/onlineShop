from django.contrib import admin
from .models import Category, Product, Order, OrderItem,ManagerProfile

admin.site.register(ManagerProfile)

# Настройка отображения категорий
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # Автоматически заполняет slug при вводе названия

# Настройка отображения товаров
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_popular']
    list_filter = ['is_popular', 'category']
    list_editable = ['price', 'is_popular']  # Можно редактировать цену и популярность прямо из списка

# Настройка отображения заказов
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Выводим только те поля, которые РЕАЛЬНО есть в нашей модели Order
    list_display = ['id', 'user', 'name', 'phone', 'city', 'address', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at', 'city']
    search_fields = ['name', 'phone', 'id']

    # Разрешаем менять статус прямо из списка заказов
    list_editable = ['status']

    # Позволяет видеть товары внутри заказа прямо на странице редактирования
    inlines = [OrderItemInline]