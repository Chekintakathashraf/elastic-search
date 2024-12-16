import os
import django
from faker import Faker
import random
from django.utils.text import slugify

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elasticproject.settings')
django.setup()

from products.models import Product, Tags

fake = Faker()

def create_tags():
    tag_objects = []
    for _ in range(20):  
        tag_name = fake.unique.word()
        tag, created = Tags.objects.get_or_create(tag=tag_name)
        tag_objects.append(tag)
    return tag_objects

def create_products():
    tags = create_tags() 
    products = []

    for _ in range(100): 
        title = fake.sentence(nb_words=3)
        description = fake.paragraph(nb_sentences=5)
        category = random.choice(['Electronics', 'Fashion', 'Home', 'Toys', 'Sports', 'Books'])
        price = round(random.uniform(5.0, 1000.0), 2)
        brand = fake.company() if random.choice([True, False]) else None
        sku = fake.unique.bothify(text='??-####-##')
        thumbnail = fake.image_url()
      
        product = Product.objects.create(
            title=title,
            description=description,
            category=slugify(category),
            price=price,
            brand=slugify(brand),
            sku=sku,
            thumbnail=thumbnail,
        )
        
        product.tags.set(random.sample(tags, k=random.randint(1, 5)))
        
        products.append(product)
    
    print("100 Fake Products Created Successfully!")

if __name__ == "__main__":
    create_products()
