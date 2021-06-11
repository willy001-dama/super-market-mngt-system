import random
import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView, PasswordResetView)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.generic import DetailView
from django.utils import timezone


from . import models, utils
from . import forms
from .forms import ContactUsForm
from .models import Product, Order, OrderItem, Profile, Message, Sale
from .utils import generate_ref_code

TODAY = str(datetime.date.today())
PAST_SEVEN_DAYS = str(datetime.date.today() - datetime.timedelta(days=7))[:10]
THIS_MONTH = None
THIS_YEAR = None


def login_view(request):
    """function base login view"""
    error = False
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('/')
            elif user.is_staff:
                return redirect('/products/')
            else:
                return redirect('/shopping/')
        else:
            error = True

    context = {'error': error}
    template_name = 'account/login.html'
    return render(request, template_name, context)


@login_required()
def logout_view(request):
    """function base logout view"""
    logout(request)
    return redirect('/')


class ChangePassword(PasswordChangeView):
    """class based view for changing password"""
    template_name = 'account/password_change.html'
    success_url = '/profile/'

    def get_context_data(self, **kwargs):
        kwargs['section'] = 'Profile'
        return super().get_context_data(**kwargs)


class PasswordReset(PasswordResetView):
    """class base view for resetting user password"""
    template_name = 'account/password_reset.html'


@login_required()
def profile(request):
    user_id = request.user.id
    user_profile = models.Profile.objects.get(user=user_id)
    all_user = models.Profile.objects.exclude(user=user_id)
    context = {'profile': user_profile, 'all_user': all_user, 'section': 'Profile'}
    return render(request, 'account/profile.html', context)


@login_required()
def delete_user(request, pk):
    models.Profile.objects.get(pk=pk).delete()
    messages.success(request, 'Member has been deleted successfully')
    return redirect('/profile/')


@login_required()
def member_profile(request, pk):
    user_profile = models.Profile.objects.get(pk=pk)
    context = {'section': 'Profile', 'user': user_profile}
    return render(request, 'account/member_profile.html', context)


@login_required()
def add_user(request):
    """function for adding new user"""
    if request.method == "POST":
        base_user_form = forms.ProfileForm(request.POST, request.FILES)
        if base_user_form.is_valid():
            base_user_form = base_user_form.cleaned_data

            user = User.objects.create_user(username=base_user_form['first_name'],
                                            password='Yun,?-RqPgkV%|I]',
                                            email=base_user_form['email'],
                                            )
            user.first_name = base_user_form['first_name']
            user.last_name = base_user_form['last_name']
            user.is_staff = True
            user.save()
            user_profile = models.Profile.objects.create(user=user, phone=base_user_form['phone'],
                                                         address=base_user_form['address'],
                                                         rank=base_user_form['rank'],
                                                         gender=base_user_form['gender'],
                                                         state=base_user_form['state'],
                                                         image=base_user_form['image']
                                                         )
            messages.success(request, f'Member {user_profile} added successfully')
            return redirect('/profile/')
        else:
            base_user_form = forms.ProfileForm()
    else:
        base_user_form = forms.ProfileForm()

    context = {'user_form': base_user_form, 'section': 'Profile'}
    return render(request, 'account/add_user.html', context)


def customer_creation(request):
    if request.method == "POST":
        username = request.POST.get('first_name') + request.POST.get('last_name')

        password = 'Yun,?-RqPgkV%|I]'
        print(username, ' ', password)

        user = User.objects.create_user(username,
                                        request.POST.get('email'), password,
                                        )
        if user:
            user.first_name = request.POST.get('first_name'),
            user.last_name = request.POST.get('last_name')
            user.save()
            credential = {'username': username, 'password': password}
            messages.success(request, f'Customer {user} added successfully')
            # return redirect('/customer/account/')
    else:
        credential = None
        error = True
    context = {'section': 'Profile', 'info': credential}
    return render(request, 'account/user_creation.html', context)


# ----------------------------------------------------------------
@login_required()
def user_update(request, pk):
    user_profile = get_object_or_404(models.Profile, pk=pk)
    if request.method == 'POST':
        update_form = forms.UserUpdateForm(request.POST, request.FILES,
                                           instance=user_profile)
        if update_form.is_valid():
            print('form is valid')
            update_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('/profile/')
        else:
            print('form is not valid')
    else:
        print('not a post method')
        update_form = forms.UserUpdateForm(instance=user_profile)
    context = {'form': update_form, 'section': 'Profile'}
    return render(request, 'account/update_profile.html', context)


@login_required()
def homepage(request):
    """home page"""
    utils.investment_pie()
    utils.monthly_sales_graph()
    categories = [items.category for items in models.Product.objects.all()]
    total_product = models.TotalProduct.objects.all().count()
    sales = models.Sale.objects.all().count()

    try:
        total_sale_price = models.TotalSalesPrice.objects.all()[0]
    except IndexError:
        total_sale_price = 0

    product = models.Product.objects.all().count()
    context = {'section': 'Dashboard', 'total': total_product, 'sales': sales,
               'product': product, 'sales_price': total_sale_price,
               'categories': set(categories)}
    return render(request, 'home.html', context)


# --------------------------------------------------------------------------------------
@login_required()
def sales_page(request):
    """view all the sale."""
    if request.method == 'POST':
        value = request.POST.get('search')
        query_set = models.Sale.objects.filter(name__icontains=value)
        total_price = 0
        total_price = [total_price + x.price for x in query_set]
        total_goods_found = query_set.count()

        context = {'section': 'Sales', 'page_object': query_set, 'total_price': total_price,
                   'goods_sold': total_goods_found}
        return render(request, 'sales.html', context)
    else:
        response = request.GET.get('date')
        if response:  # if an option selected,
            if response == 'any':  # if all, return all products
                sale_record = models.Sale.objects.all()
                filters = 'any'
            elif response == 'today':  # if other choice, perform the query directly
                sale_record = models.Sale.objects.filter(date=TODAY)
                filters = 'today'
            elif response == 'seven':  # if other choice, perform the query directly
                sale_record = models.Sale.objects.filter(date__gt=PAST_SEVEN_DAYS)
                filters = 'seven days'
            elif response == 'month':  # if other choice, perform the query directly
                sale_record = models.Sale.objects.filter(date='2020-03-01')
                filters = 'this month'
            elif response == 'year':  # if other choice, perform the query directly
                sale_record = models.Sale.objects.filter(date__icontains=str(timezone.now().year))
                filters = 'this year'
            else:
                sale_record = models.Sale.objects.all()
                filters = 'any'
        else:  # if response is empty just return all product
            sale_record = models.Sale.objects.all()
            filters = 'any'

        try:
            total_price = models.TotalSalesPrice.objects.all()[0]
        except IndexError:
            total_price = 0
        total_goods_sold = sale_record.count()
        paginator = Paginator(sale_record, 12)  # 12 sales in each page
        page = request.GET.get('page')
        try:
            page_object = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            page_object = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            page_object = paginator.page(paginator.num_pages)

        context = {'section': 'Sales', 'page_object': page_object,
                   'total_price': total_price, 'goods_sold': total_goods_sold,
                   'filter': filters}
        return render(request, 'sales.html', context)


@login_required()
def add_sales_record(request):
    if request.method == 'POST':
        record_form = forms.AddSaleForm(request.POST, request.FILES)
        if record_form.is_valid():
            record_form.save()
            return redirect('/sales/')
        else:
            record_form = forms.AddSaleForm()
    else:
        record_form = forms.AddSaleForm()
    context = {'section': 'Sales', 'form': record_form}
    return render(request, 'add_sales.html', context)


class SaleDetailView(DetailView):
    """class base view for single sale record"""
    context_object_name = 'record'
    template_name = 'single_sale.html'
    model = models.Sale

    def get_context_data(self, **kwargs):
        kwargs['section'] = 'Sales'
        return super().get_context_data(**kwargs)


@login_required()
def delete_sale_record(request, pk):
    """view to delete single sale record"""
    models.Sale.objects.get(pk=pk).delete()
    messages.success(request, 'Sale record deleted successfully')
    return redirect('/sales/')


def edit_sale_record(request, pk):
    """view for editing the sale record"""
    sale_record = get_object_or_404(models.Sale, pk=pk)  # get the record using pk
    if request.method == 'POST':
        update_form = forms.EditSalesForm(request.POST, request.FILES,
                                          instance=sale_record)
        if update_form.is_valid():  # if form is valid
            update_form.save()  # save the record
            messages.success(request, 'record has been edited successfully')
            return redirect('/sales/')  # redirect to sale page with success message
        else:
            print('form is not valid')
    else:  # if no data submitted, create form for update
        print('not a post method')
        update_form = forms.EditSalesForm(instance=sale_record)
    context = {'form': update_form}
    return render(request, 'update_sale.html', context)


# --------------------------------------------------------------------------------------------
@login_required()
def product_page(request):
    """view all the product."""
    # get all the category in the product to be used by the category form in template
    categories = [items.category for items in models.Product.objects.all()]
    response = request.GET.get('category')  # get the selected option from user
    print(categories, response)
    if request.method == 'POST':  # if search form submitted
        value = request.POST.get('search')  # get the search value
        # perform query
        query_set = models.Product.objects.filter(name__icontains=value)
        total_price = 0  # initialize value for total price
        # iterate through the query set and add all the prices
        total_price = [total_price + x.price for x in query_set]
        # get number of products base on search
        total_goods_found = query_set.count()
        context = {'section': 'Product', 'products': query_set, 'total_price': total_price,
                   'goods_sold': total_goods_found}
        return render(request, 'products.html', context)

    else:  # if not a post method
        if response:  # if an option selected,
            if response == 'all':  # if all, return all products
                products = models.Product.objects.all()
            else:  # if other choice, perform the query directly
                try:
                    # using try to catch error
                    products = models.Product.objects.filter(category__icontains=response.lower())
                    if not products:  # since filter method does not raise error, check if it empty
                        products = models.Product.objects.all()  # return all product
                finally:  # finally just pass
                    pass
        else:  # if response is empty just return all product
            products = models.Product.objects.all()

        context = {'products': products, 'section': 'Products',
                   'categories': set(categories)}
        return render(request, 'products.html', context)


class ProductDetailView(DetailView):
    """class base view for single product record"""
    context_object_name = 'record'
    template_name = 'product_details.html'
    model = models.Product

    def get_context_data(self, **kwargs):
        kwargs['section'] = 'Product'
        return super().get_context_data(**kwargs)


@login_required()
def delete_product_record(request, pk):
    """view to delete single product record"""
    models.Product.objects.get(pk=pk).delete()
    messages.success(request, 'product deleted successfully')
    return redirect('/products/')


@login_required()
def add_product_record(request):
    if request.method == 'POST':
        record_form = forms.AddProductForm(request.POST, request.FILES)
        if record_form.is_valid():
            record_form.save()
            messages.success(request, 'product added successfully!')
            return redirect('/products/')
        else:
            record_form = forms.AddProductForm()
    else:
        record_form = forms.AddProductForm()
    context = {'section': 'Products', 'form': record_form}
    return render(request, 'add_product.html', context)


@login_required()
def edit_product_record(request, pk):
    product = get_object_or_404(models.Product, pk=pk)
    if request.method == 'POST':
        update_form = forms.EditProductForm(request.POST, request.FILES, instance=product)
        if update_form.is_valid():
            update_form.save()
            return redirect('/product/')
        else:
            pass
    else:
        update_form = forms.EditProductForm(instance=product)
    context = {'form': update_form}
    return render(request, 'update_product.html', context)


@login_required
def shopping(request):
    ordered = [item.product.name for item in Order.objects.filter(owner=request.user.id)]
    categories = [items.category for items in models.Product.objects.all()]
    response = request.GET.get('category')  # get the selected option from user
    print(categories, response)
    if request.method == 'POST':  # if search form submitted
        value = request.POST.get('search')  # get the search value
        # perform query
        query_set = models.Product.objects.filter(name__icontains=value)
        context = {'section': 'Product', 'product': query_set, 'order': ordered}
        return render(request, 'shopping.html', context)

    else:  # if not a post method
        if response:  # if an option selected,
            if response == 'all':  # if all, return all products
                products = models.Product.objects.all()
            else:  # if other choice, perform the query directly
                try:
                    # using try to catch error
                    products = models.Product.objects.filter(category__icontains=response.lower())
                    if not products:  # since filter method does not raise error, check if it empty
                        products = models.Product.objects.all()  # return all product
                finally:  # finally just pass
                    pass
        else:  # if response is empty just return all product
            products = models.Product.objects.all()
    context = {'section': 'Shopping', 'product': products, 'order': ordered, 'categories': set(categories)}
    return render(request, 'shopping.html', context)


@login_required()
def add_to_cart(request, pk):
    user = request.user
    item = Product.objects.get(pk=pk)
    order = Order.objects.create(product=item, owner=user)
    order_item, status = OrderItem.objects.get_or_create(owner=user, )
    order_item.items.add(order)
    order.ref_id = random.randint(0, 100)
    order.save()
    return redirect('/shopping/')


@login_required()
def delete_from_cart(request, pk):
    user = request.user.id
    product = get_object_or_404(Product, pk=pk)
    item = Order.objects.filter(product__name=product, owner=user, )[0]
    order_item = OrderItem.objects.get(owner=user)
    order_item.items.remove(item)
    order_item.save()
    item.delete()
    return redirect('/shopping/')


def delete_from_cart2(request, pk):
    user = request.user.id
    product = get_object_or_404(Product, pk=pk)
    item = Order.objects.filter(product__name=product, owner=user, )[0]
    order_item = OrderItem.objects.get(owner=user)
    order_item.items.remove(item)
    order_item.save()
    item.delete()
    return redirect('/check_out/')


@login_required()
def cancel_selection(request):
    user = request.user.id
    order = Order.objects.filter(owner=user)
    order.delete()
    order_item = OrderItem.objects.get(owner=user)
    order_item.delete()
    del order
    return redirect('/shopping/')


@login_required()
def check_out(request):
    user = request.user.pk
    try:
        order_list = OrderItem.objects.get(owner=user).items.all()
    except:
        order_list = None
        price = None
        quantity = None
    else:
        price = f'{sum([item.product.price for item in order_list]):,}'
        quantity = order_list.count()

    context = {'item': order_list,
               'section': 'Check out',
               'price': price, 'q': quantity}
    return render(request, 'check_out.html', context)


def generate_reference(request):
    user = request.user.pk
    code = generate_ref_code()
    order_list = OrderItem.objects.get(owner=user)
    all_order_list = [order.ref_id for order in OrderItem.objects.all()]
    if code in all_order_list:
        code = generate_ref_code()
    else:
        pass

    print(all_order_list)
    try:
        order_list.ref_id = code
    except:
        order_list.ref_id = generate_ref_code()

    order_list.save()
    print(code)
    context = {'code': code, 'section': 'Reference code'}
    return render(request, 'reference.html', context)


def contact_us(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print('form is not valide')
            print(form)
            pass
        messages.success(request, 'Your message was sent successfully.')
        pass
    else:
        pass
    context = {'section': 'Contact'}
    return render(request, 'contact.html', context)


def message(request):
    message_ = Message.objects.all()
    context = {'section': 'Message', 'message': message_}
    return render(request, 'message.html', context)


def delete_message(request, pk):
    if request.user.is_staff:
        Message.objects.get(pk=pk).delete()

    return redirect('/messages/')


def add_sales_from_ref(request):
    if request.method == 'POST':
        ref_code = request.POST.get('reference')
        item = get_object_or_404(OrderItem, ref_id=ref_code).items.all()
        price = f'{sum([item.product.price for item in item]):,}'

    else:
        item = None
        price = None
        ref_code = None
    context = {'item': item, 'price': price, 'ref_code': ref_code,
               'section': 'Add Sales from Reference Code'}
    print(item)
    return render(request, 'add_from_ref.html', context)


def save_sales_to_db(request, ref):
    order_items = get_object_or_404(OrderItem, ref_id=ref)
    user = Profile.objects.get(pk=request.user.id)
    for item in order_items.items.all():
        Sale.objects.create(name=item.product.name, price=item.product.price,
                            category=item.product.category,
                            sub_category=item.product.sub_category,
                            supplier=item.product.supplier, quantity=1,
                            picture=item.product.picture)
        print('done', item)
        order_items.items.remove(item)
    order_items.save()
    Order.objects.filter(owner=user).delete()
    return redirect('/sales/')
