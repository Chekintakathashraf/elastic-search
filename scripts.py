import os

import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'elasticproject.settings'
django.setup()
import django

from products.models import Product, Brand

from products.documents import ProductDocument


products = Product.objects.all()

for product in products:
    try:
        brand , _ = Brand.objects.get_or_create(brand_name = product.brand)
        product.brand_name = brand
        product.save()
    except Exception as e:
        print(e)

