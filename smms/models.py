import os
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

# Create your models here.
GENDER = (('Male', 'Male'), ('Female', 'Female'))


def path_to_images(instance, filename):
    return os.path.join('picture', str(instance), filename)


class Costumer(models.Model):
    """table for customer"""
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gender = models.CharField(choices=GENDER, max_length=10, default=GENDER[0])
    phone = models.CharField(max_length=12)
    rank = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
    image = models.ImageField(upload_to=path_to_images, null=True, blank=True)
    state = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.user}'

    def get_full_name(self):
        """return fullname of user"""
        if self.user.first_name and self.user.last_name:  # if user has first and last name
            full_name = self.user.first_name + ' ' + self.user.last_name  # join the and return
        else:
            full_name = self.user.username  # if no first and last name retur username
        return full_name  # return the final fullname

    def get_email(self):
        """return user image from user models"""
        if self.user.email:
            return self.user.email
        else:
            return None

    def get_image(self):
        """
            get the user image. if no image,
            return link to default image to be use
        """
        no_image = '/static/no_pic.png'
        if self.image.url:
            image = self.image.url
        else:
            image = no_image
        return image


class TotalProduct(models.Model):
    """
        model for all the product in the super market
        It keep track of imported and sells goods, keeping
        record of total number of product per category and the
        grand total.
    """
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=200,
                                    null=True, blank=True)
    quantity = models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.quantity}) ({self.price})'


class Product(models.Model):
    """models for product contained in the super market"""
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=200, null=True, blank=True)
    supplier = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    picture = models.ImageField(upload_to=path_to_images)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'

    def get_product_image(self):
        no_picture = 'path to image'
        if self.picture.url:
            image = self.picture
        else:
            image = no_picture
        return image

    def total_product(self):
        pass


# noinspection PyInterpreter
def add_to_total_product(sender, **kwargs):
    """
        signal function to add new product input to TotalProduct
        and if the item already exits, increment the price and quantity
    """
    # print(kwargs)
    if kwargs['created']:  # check if product is created successfully
        name = kwargs['instance'].name  # get product name from instance
        category = kwargs['instance'].category  # same as above
        sub_category = kwargs['instance'].sub_category  # same as above
        quantity = kwargs['instance'].quantity  # same here
        price = kwargs['instance'].price  # get product price from instance
        try:  # catch error easily
            # check if product with product name already exit in total product
            product = TotalProduct.objects.filter(name=name)
            # filter down to get product categories for secure query
            final_product = product.filter(category=category)
            if sub_category:  # check if product has sub_category
                try:  # check if product has sub_category
                    final_product = final_product.get(sub_category=sub_category)
                except:
                    print('error it just passing it')
                    pass
            else:  # if no sub_category, just pass
                pass
            final_product.quantity += quantity  # add quantity to existing quantity
            # add price to existing one but multiply with number of goods
            final_product.price += price * quantity
            # finally, save the record
            final_product.save()
            print('finally it worked')
        except ValueError:
            print('this is just a silly error')
        except KeyError:
            print('A key error occur')
        except AttributeError:  # if error, usually no file matching query
            # create a new product in the TotalProduct and add the values
            new_product = TotalProduct.objects.create(name=name,
                                                      category=category, quantity=quantity,
                                                      sub_category=sub_category, price=price * quantity
                                                      )
            new_product.save()
            print('finish saving the new product in total product')
    print(kwargs)


# signal to add the imported record to existing one
post_save.connect(add_to_total_product, sender=Product)


class Sale(models.Model):
    """models for sale record"""
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=200,
                                    null=True, blank=True)
    supplier = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    picture = models.ImageField(upload_to=path_to_images,
                                null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} {self.quantity}'

    def get_picture(self):
        """
            get the product image. if no image,
            return link to default image to be use
        """
        no_picture = '/static/no_pic.png'
        if self.picture.url:
            picture = self.picture.url
        else:
            picture = no_picture
        return picture


class Investment(models.Model):
    """total money invested in the business"""
    price = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.price}'


def populate_investment(sender, **kwargs):
    """function to populate the investment model."""
    print('in the signal phase')
    if 'created' in kwargs:  # if new record created successfully
        goods_price = kwargs['instance'].price  # get the price of the goods
        print(goods_price)
        try:
            handle: object = Investment.objects.all()[0]  # get invest model ready to populate
            handle.price += goods_price  # add new price to existing ones
            handle.save()  # save the record
        except IndexError:  # index error resulting from not object find
            Investment.objects.create(price=goods_price)  # create new entry
        print('done with it')
    else:  # if not created, just pass
        pass


# once new product are uploaded, populate the investment model
# with new price. resulting in the net price being invested in
# the business
post_save.connect(populate_investment, Product)


class TotalSalesPrice(models.Model):
    """
        total sale. Investment - total
        sales give the income/profit made
    """
    price = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.price}'


def populate_total_sales_price(sender, **kwargs):
    """function to populate the investment model."""
    print('in the signal phase')
    if 'created' in kwargs:  # if new record created successfully
        goods_price = kwargs['instance'].price  # get the price of the goods
        goods_quantity = kwargs['instance'].quantity
        total_price = goods_quantity * goods_price
        try:
            handle: object = TotalSalesPrice.objects.all()[0]  # get invest model ready to populate
            # multiply price by amount before adding to record
            handle.price += total_price  # add new price to existing ones
            handle.save()  # save the record
        except IndexError:  # index error resulting from not object find
            TotalSalesPrice.objects.create(price=total_price)  # create new entry
        except Exception as e:
            print('An error occured', e)
    else:  # if not created, just pass
        pass


# once new sales are made, add new price to
# the total amount of sells ever made
post_save.connect(populate_total_sales_price, Sale)


class Order(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    date_added = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.product}'


class OrderItem(models.Model):
    ref_id = models.CharField(max_length=15, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    items = models.ManyToManyField(Order)
    date_add = models.DateField(auto_now=True, )

    def get_cart_item(self):
        return self.items.all()

    def get_cart_total(self):
        return sum([items.product.price for items in self.items.all()])

    def __str__(self):
        return f'{self.owner} {self.ref_id}'


class Message(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
