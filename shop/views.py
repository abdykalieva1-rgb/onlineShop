from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem  # <-- ТЕПЕРЬ ОНА ЗДЕСЬ И НИКОМУ НЕ МЕШАЕТ
# 1. Главная страница
def home(request):
    # Берем категории и только популярные товары для главной страницы
    categories = Category.objects.all()
    popular_products = Product.objects.filter(is_popular=True)

    context = {
        'categories': categories,
        'products': popular_products,  # Передаем популярные товары как products
    }
    return render(request, 'shop/home.html', context)


# 2. Страница каталога


# shop/views.py
from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.db.models import Q


def catalog_page(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    # 1. Фильтр по категориям
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # 2. Фильтр по цене (ловим min_price и max_price из URL)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=int(min_price))
    if max_price:
        products = products.filter(price__lte=int(max_price))

    # 3. Фильтр по размерам (ловим список выбранных размеров)
    selected_sizes = request.GET.getlist('sizes')
    if selected_sizes:
        # Ищем товары, у которых в строке sizes содержится выбранный размер
        size_queries = Q()
        for size in selected_sizes:
            size_queries |= Q(sizes__contains=size)
        products = products.filter(size_queries)

    # 4. Фильтр по цвету
    selected_color = request.GET.get('color')
    if selected_color:
        products = products.filter(color=selected_color)

    context = {
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
        'min_price': min_price or 0,
        'max_price': max_price or 20000,
        'selected_sizes': selected_sizes,
        'selected_color': selected_color,
    }

    sort_by = request.GET.get('sort')
    if sort_by == 'cheap':
        products = products.order_by('price')  # Сначала дешевые
    elif sort_by == 'expensive':
        products = products.order_by('-price')  # Сначала дорогие
    else:
        products = products.order_by('-id')

    context = {
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
        'min_price': min_price or 0,
        'max_price': max_price or 20000,
        'selected_sizes': selected_sizes,
        'selected_color': selected_color,
        'sort_by': sort_by,  # Передаем текущую сортировку обратно в шаблон
    }
    return render(request, 'shop/catalog.html', context)


# shop/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product


# 1. Добавление товара в корзину
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product


def cart_add(request, product_id):
    # Получаем или создаем корзину в сессии
    cart = request.session.get('cart', {})

    # 1. Считываем выбранный размер из параметров (если не передан, ставим 42)
    size = request.GET.get('size', '42')

    # Создаем уникальный ключ для товара с учетом его размера (например: "5_42")
    item_key = f"{product_id}_{size}"

    if item_key in cart:
        cart[item_key]['quantity'] += 1
    else:
        cart[item_key] = {
            'product_id': product_id,
            'quantity': 1,
            'size': size
        }

    request.session['cart'] = cart
    return redirect('shop:cart_detail')  # или как называется твой URL корзины


def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for item_key, item_data in cart.items():
        # БЕЗОПАСНО КЛЮЧУЕМ ID ТОВАРА:
        # Если в item_data есть 'product_id' — берем его.
        # Если нет (это старый формат), то ID товара — это сам item_key.
        product_id = item_data.get('product_id', item_key)

        # Получаем товар из базы данных
        product = get_object_or_404(Product, id=product_id)

        # Считаем стоимость
        item_total = product.price * item_data['quantity']
        total_price += item_total

        # Безопасно достаем размер (если старый формат — поставим по дефолту '42')
        size = item_data.get('size', '42')

        cart_items.append({
            'product': product,
            'quantity': item_data['quantity'],
            'size': size,
            'item_key': item_key
        })

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'shop/cart.html', context)


def cart_minus(request, item_key):
    cart = request.session.get('cart', {})

    if item_key in cart:
        if cart[item_key]['quantity'] > 1:
            cart[item_key]['quantity'] -= 1
        else:
            # Если остался всего 1 товар, то при нажатии на минус удаляем его совсем
            del cart[item_key]

        request.session['cart'] = cart

    return redirect('shop:cart_detail')

# 2. Удаление товара из корзины
def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart

    return redirect('shop:cart_detail')


from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
import urllib.parse


def register_view(request):
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким логином уже существует.')
            return redirect('shop:register')

        # Создаем пользователя
        user = User.objects.create_user(username=username, email=email, password=password)
        auth_login(request, user)  # Автоматически авторизуем после регистрации
        return redirect('shop:home')

    return render(request, 'shop/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('shop:home')
        else:
            messages.error(request, 'Неверный логин или пароль.')
            return redirect('shop:login')

    return render(request, 'shop/login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('shop:home')
import random
import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Product, Order, OrderItem

@login_required(login_url='shop:login')
@transaction.atomic
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    total_quantity = 0

    # Собираем данные из корзины
    for item_key, item_data in cart.items():
        product_id = item_data.get('product_id', item_key)
        product = get_object_or_404(Product, id=product_id)

        item_total = product.price * item_data['quantity']
        total_price += item_total
        total_quantity += item_data['quantity']

        cart_items.append({
            'product': product,
            'quantity': item_data['quantity'],
            'size': item_data.get('size', '42'),
        })

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        address = request.POST.get('address')

        # 1. Сохраняем заказ в базу данных напрямую (БЕЗ ПРОВЕРКИ НАЛИЧИЯ)
        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            city=city,
            address=address,
            total_price=total_price
        )

        # Сохраняем все товары из корзины в этот заказ
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                size=item['size']
            )

        # 2. Формируем красивый текст сообщения для WhatsApp
        message = (
            f"🔔 *НОВЫЙ ЗАКАЗ LI-NING!* 🔔\n\n"
            f"📦 *Номер заказа:* #{order.id}\n"
            f"👤 *Покупатель:* {name} (Логин: {request.user.username})\n"
            f"📞 *Телефон:* {phone}\n"
            f"📍 *Адрес:* {city}, {address}\n\n"
            f"👟 *Товары:*\n"
        )

        for item in cart_items:
            product = item['product']
            chosen_size = str(item['size']).strip()
            quantity = item['quantity']

            message += f"▪️ {product.name} (Разм: {chosen_size}) — {quantity} шт. x {product.price} сом\n"

            # ЛОГИКА УДАЛЕНИЯ РАЗМЕРА ИЗ СТРОКИ SIZES
            if product.sizes:
                current_sizes = [s.strip() for s in product.sizes.split(',') if s.strip()]

                if chosen_size in current_sizes:
                    current_sizes.remove(chosen_size)
                    product.sizes = ",".join(current_sizes)
                    product.save()

        message += f"\n💰 *Итого к оплате:* {total_price} сом"

        # Кодируем текст для ссылки
        encoded_message = urllib.parse.quote(message)

        # Твои 4 номера менеджеров
        whatsapp_numbers = [
            "996500070629",
            "996501358735",
            "996707319213",
            "996704215450"
        ]
        chosen_phone = random.choice(whatsapp_numbers)
        whatsapp_url = f"https://api.whatsapp.com/send?phone={chosen_phone}&text={encoded_message}"

        # Очищаем корзину в сессии
        request.session['cart'] = {}
        request.session.modified = True

        return redirect(whatsapp_url)

    # Отображение страницы оформления для GET-запроса
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity,
    }
    return render(request, 'shop/checkout.html', context)




@login_required(login_url='shop:login')  # Если пользователь не вошел, Django перекинет его на логин
def profile_view(request):
    user_orders = request.user.orders.all().order_by('-created_at')
    context = {
        'orders': user_orders,
    }
    return render(request, 'shop/profile.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import Order, Product


@login_required(login_url='shop:login')
def admin_dashboard(request):
    # Строгая проверка по базе данных: входит ли пользователь в группу "Сотрудники"
    is_employee = request.user.groups.filter(name='Сотрудники').exists()

    # Разрешаем доступ, только если он в группе "Сотрудники" или является главным суперпользователем
    if not (is_employee or request.user.is_superuser):
        # Если человека нет в базе сотрудников, отдаем шаблон с ошибкой доступа
        return render(request, 'shop/access_denied.html', {
            'username': request.user.username,
            'full_name': request.user.get_full_name()
        })

    # ЕСЛИ ЧЕЛОВЕК НАЙДЕН В БАЗЕ — ЗАГРУЖАЕМ ДАННЫЕ ДЛЯ МАКЕТА:
    total_orders_count = Order.objects.count()
    total_customers_count = User.objects.filter(is_staff=False).count()

    # Считаем реальную выручку
    revenue_data = Order.objects.aggregate(total=Sum('total_price'))
    total_revenue = revenue_data['total'] if revenue_data['total'] else 0
    total_products_count = Product.objects.count()
    recent_orders = Order.objects.all().order_by('-id')[:5]

    # Данные для графика
    chart_labels = []
    chart_data = []
    today = timezone.now().date()

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        chart_labels.append(day.strftime('%d %b'))
        day_revenue = Order.objects.filter(created_at__date=day).aggregate(total=Sum('total_price'))['total'] or 0
        chart_data.append(float(day_revenue))

    context = {
        'total_orders': total_orders_count,
        'total_customers': total_customers_count,
        'total_revenue': total_revenue,
        'total_products': total_products_count,
        'recent_orders': recent_orders,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'shop/admin_dashboard.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# Импортируем модель категории, если она называется Category
from .models import Product, Category


@login_required(login_url='shop:login')
def admin_products(request):
    ALLOWED_EMPLOYEES = ['meder', 'elida', 'boss_lining', 'worker_1']
    if request.user.username not in ALLOWED_EMPLOYEES:
        return render(request, 'shop/access_denied.html', {'username': request.user.username})

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. ДОБАВЛЕНИЕ ТОВАРА
        if action == 'add':
            name = request.POST.get('name')
            price = request.POST.get('price')
            image = request.FILES.get('image')

            if name and price:
                # Находим самую первую категорию в базе данных, чтобы привязать товар к ней
                default_category = Category.objects.first()

                # Если в базе вообще нет категорий, создадим временную "Обувь"
                if not default_category:
                    default_category = Category.objects.create(name="Обувь")

                # Передаем категорию при создании
                Product.objects.create(
                    name=name,
                    price=price,
                    image=image,
                    category=default_category
                )
            return redirect('shop:admin_products')

        # 2. ИЗМЕНЕНИЕ ТОВАРА
        elif action == 'edit':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)

            product.name = request.POST.get('name')
            product.price = request.POST.get('price')
            if request.FILES.get('image'):
                product.image = request.FILES.get('image')

            # На всякий случай проверяем категорию и при изменении
            if not product.category_id:
                default_category = Category.objects.first() or Category.objects.create(name="Обувь")
                product.category = default_category

            product.save()
            return redirect('shop:admin_products')

        # 3. УДАЛЕНИЕ ТОВАРА
        elif action == 'delete':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            return redirect('shop:admin_products')

    products = Product.objects.all().order_by('-id')
    return render(request, 'shop/admin_products.html', {'products': products})



















from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required(login_url='shop:login')
def admin_users(request):
    # Защитный белый список сотрудников
    ALLOWED_EMPLOYEES = ['meder', 'elida', 'boss_lining', 'worker_1']
    if request.user.username not in ALLOWED_EMPLOYEES:
        return render(request, 'shop/access_denied.html', {'username': request.user.username})

    # ОБРАБОТКА ИЗМЕНЕНИЯ И УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЕЙ
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        customer = get_object_or_404(User, id=user_id)

        # 1. ИЗМЕНЕНИЕ ПОЛЬЗОВАТЕЛЯ (Логин и Email)
        if action == 'edit':
            customer.username = request.POST.get('username_field')
            customer.email = request.POST.get('email')
            customer.save()
            return redirect('shop:admin_users')

        # 2. УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
        elif action == 'delete':
            # Защита: не разрешаем пользователю удалить самого себя
            if customer.id != request.user.id:
                customer.delete()
            return redirect('shop:admin_users')

    # Получаем всех пользователей сайта (сортируем: новые вверху)
    customers = User.objects.all().order_by('-id')
    return render(request, 'shop/admin_users.html', {'customers': customers})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# Убедись, что модель заказа называется Order (или скорректируй под свой проект)
from .models import Order

@login_required(login_url='shop:login')
def admin_orders(request):
    # Наш список сотрудников
    ALLOWED_EMPLOYEES = ['meder', 'elida', 'boss_lining', 'worker_1']
    if request.user.username not in ALLOWED_EMPLOYEES:
        return render(request, 'shop/access_denied.html', {'username': request.user.username})

    # ОБРАБОТКА ДЕЙСТВИЙ С ЗАКАЗАМИ
    if request.method == 'POST':
        action = request.POST.get('action')
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)

        # 1. ИЗМЕНЕНИЕ СТАТУСА ЗАКАЗА
        if action == 'edit_status':
            new_status = request.POST.get('status')
            if new_status:
                order.status = new_status
                order.save()
            return redirect('shop:admin_orders')

        # 2. УДАЛЕНИЕ ЗАКАЗА
        elif action == 'delete':
            order.delete()
            return redirect('shop:admin_orders')

    # Получаем все заказы: самые новые будут отображаться первыми
    orders = Order.objects.all().order_by('-id')
    return render(request, 'shop/admin_orders.html', {'orders': orders})