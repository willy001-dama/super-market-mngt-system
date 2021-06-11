import os
import random
from datetime import datetime
from time import sleep

import matplotlib.pyplot as plt
import numpy as np

from django.conf import settings
from .models import Investment, TotalSalesPrice, Sale


def investment_pie():
    try:
        invest_value = Investment.objects.all()[0].price
        sale_value = TotalSalesPrice.objects.all()[0].price
    except IndexError:
        invest_value = 0
        sale_value = 0
    print('this is the investment pie', invest_value, sale_value)
    profit = sale_value - invest_value
    if profit < 0:
        profit = 0
    x = [invest_value, sale_value, profit]
    print(invest_value)
    print(sale_value)
    print(profit)
    print(x)
    try:
        base, text = plt.pie(x, colors=['tomato', 'orange', 'red'], )
        plt.legend(['Investment', 'Sales', 'Profit'], loc='upper left')
        path = os.path.join(settings.BASE_DIR, 'smms', 'static', 'pie.png')
        plt.savefig(path, bbox_inches='tight')
        plt.close()
    except ValueError:
        pass
    return None


def monthly_sales_graph():
    year = int(datetime.today().year)
    jan_first = datetime(year, 1, 11)
    jan = datetime(year, 1, 31)
    feb = datetime(year, 2, 28)
    mar = datetime(year, 3, 31)
    apr = datetime(year, 4, 30)
    may = datetime(year, 5, 31)
    jun = datetime(year, 6, 30)
    jul = datetime(year, 7, 31)
    aug = datetime(year, 8, 31)
    sep = datetime(year, 9, 30)
    oct = datetime(year, 10, 31)
    nov = datetime(year, 11, 30)
    dec = datetime(year, 12, 31)
    jan_sales = sum([1 + i.price for i in Sale.objects.filter(date__gte=jan_first,
                                                              date__lte=jan)])
    feb_sales = sum([1 + i.price for i in Sale.objects.filter(date__gt=jan,
                                                              date__lte=feb)])
    mar_sales = sum([1 + i.price for i in Sale.objects.filter(date__gt=feb,
                                                              date__lte=mar)])
    apr_sales = sum([1 + i.price for i in Sale.objects.filter(date__gt=mar,
                                                              date__lte=apr)])
    may_sales = sum([1 + i.price for i in Sale.objects.filter(date__gt=apr,
                                                              date__lte=may)])
    jun_sales = sum([1 + i.price for i in Sale.objects.filter(date__gt=may,
                                                              date__lte=jun)])
    jul_sales = sum([1 + i.price for i in Sale.objects.filter(date__gt=jun,
                                                              date__lte=jul)])
    aug_sales = sum([1 + i.price for i in Sale.objects.filter(date__gt=jul,
                                                              date__lte=aug)])
    sep_sales = sum([1 + i.price for i in Sale.objects.filter(date__gt=aug,
                                                              date__lte=sep)])
    oct_sales = sum([20 + i.price for i in Sale.objects.filter(date__gt=sep,
                                                               date__lte=oct)])
    nov_sales = sum([10 + i.price for i in Sale.objects.filter(date__gt=oct,
                                                               date__lte=nov)])
    dec_sales = sum([500 + i.price for i in Sale.objects.filter(date__gt=nov,
                                                                date__lte=dec)])
    y = [jan_sales, feb_sales, mar_sales, apr_sales, may_sales, jun_sales,
         jul_sales, aug_sales, sep_sales, oct_sales, nov_sales, dec_sales]
    x_ticks = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
               'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    print(y)
    x = range(len(x_ticks))
    plt.bar(x, y, align='center', alpha=0.5, color='tomato')
    plt.xticks(x, x_ticks)
    plt.ylabel = 'Price'
    plt.xlabel = 'Month'
    plt.title('Sales Per Month')
    plt.legend([])
    path = os.path.join(settings.BASE_DIR, 'smms', 'static', 'bar.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    sleep(2)
    return None


def weekly_sales_graph():
    pass


def generate_ref_code():
    code = ''
    for i in range(10):
        code += str(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]))
        print(code)
    print(code)
    return code
