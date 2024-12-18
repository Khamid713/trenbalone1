from django.shortcuts import render, redirect
from .models import Category, Product, Cart
from .forms import RegForm
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
import telebot

# Создаем объект бота
bot = telebot.TeleBot('7590979500:AAFI-1b_cs-vNnSZCcuBRq91zaakL9GJdn4')


# Create your views here.
# Главная страница
def home_page(request):
    # Достаем данные из БД
    products = Product.objects.all()
    categories = Category.objects.all()
    # Передаем данные на Frontend
    context = {'products': products, 'categories': categories}

    return render(request, 'home.html', context)


# Вывод товаров по выбранной категории
def category_page(request, pk):
    # Достаем выбранную категорию
    category = Category.objects.get(id=pk)
    # Фильтруем товары по категории
    products = Product.objects.filter(product_category=category)
    print(products)
    # Передаем данные на Frontend
    context = {'category': category, 'products': products}

    return render(request, 'category.html', context)


# Вывод определенного товара
def product_page(request, pk):
    # Вывод выбранного товара
    product = Product.objects.get(id=pk)
    # Передаем данные на Frontend
    context = {'product': product}

    return render(request, 'product.html', context)


# Класс представления (Регистрация)
class Register(View):
    template_name = 'registration/register.html'

    # Выдача формы
    def get(self, request):
        context = {'form': RegForm}
        return render(request, self.template_name, context)


    # Получение инфы с формы
    def post(self, request):
        form = RegForm(request.POST)

        # Если данные корректны
        if form.is_valid():
            username = form.clean_username()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password2')

            # Создаем объект класса User
            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)
            print(user)
            user.save()

            # Авторизуем пользователя
            login(request, user)
            return redirect('/')
        # Если данные некорректны
        context = {'form': RegForm, 'message': 'Пароль или почта неверны!'}
        return render(request, self.template_name, context)


# Поиск
def search(request):
    if request.method == 'POST':
        get_product = request.POST.get('search')

        if Product.objects.get(product_name__iregex=get_product):
            searched_product = Product.objects.get(product_name__iregex=get_product)
            return redirect(f'/product/{searched_product.id}')
        else:
            return redirect('/')


# Выход из аккаунта
def logout_view(request):
    logout(request)
    return redirect('/')


# Добавление товара в корзину
def to_cart(request, pk):
    if request.method == 'POST':
        product = Product.objects.get(id=pk)
        if product.product_count >= int(request.POST.get('product_amount')):
            Cart.objects.create(user_id=request.user.id,
                                user_product=product,
                                user_pr_count=int(request.POST.get('product_amount'))).save()
            return redirect('/')


# Удаление товара из корзины
def del_from_cart(request, pk):
    product_to_del = Product.objects.get(id=pk)
    Cart.objects.filter(user_product=product_to_del).delete()

    return redirect('/cart')


# Отображение корзины
def cart_page(request):
    user_cart = Cart.objects.filter(user_id=request.user.id)
    product_ids = [i.user_product.id for i in user_cart]
    user_pr_counts = [j.user_pr_count for j in user_cart]
    pr_stocks = [c.user_product.product_count for c in user_cart]
    totals = [round(t.user_pr_count * t.user_product.product_price, 2) for t in user_cart]
    text = (f'Новый заказ!\n'
            f'Клиент: {User.objects.get(id=request.user.id).email}\n\n')


    if request.method == 'POST':
        for i in range(len(product_ids)):
            product = Product.objects.get(id=product_ids[i])
            product.product_count = pr_stocks[i] - user_pr_counts[i]
            product.save(update_fields=['product_count'])

        for j in user_cart:
            text += (f'Товар: {j.user_product}\n'
                     f'Количество: {j.user_pr_count}\n'
                     f'---------------------------------------\n')


        text += f'Итого: ${round(sum(totals), 2)}'
        bot.send_message(6775701667, text)
        user_cart.delete()
        return redirect('/')

    context = {'cart': user_cart, 'total': round(sum(totals), 2)}
    return render(request, 'cart.html', context)











