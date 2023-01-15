from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Customer, Collection, Order, OrderItem


# Create your views here.
# Request handler
# Request -> response

def say_hello(request):
    # Product.objects returns a "Manager" (Interface to DB) with methods 
    # that return a query_set
    query_set = Product.objects.all()

    # query sets are "lazy" cause evaluated at a later point
    # they are useful for complex filters 
    # or to get e.g. only the first five products are read from DB:
    for product in query_set[0:5]:
        print(product)

    product1 = Product.objects.get(pk=1)

    # if a product does not exist by id, exception will be thrown
    try:
        product_not_exist = Product.objects.get(pk=0)
    except ObjectDoesNotExist:
        pass

    # but filter with first() method will deliver a non, if product does not 
    # exist, instead of throwing exception
    product_none = Product.objects.filter(pk=1).first()
    print(product_none)

    # check existence
    exists = Product.objects.filter(pk=42).exists()
    print(product_none)

    # filter 
    product_price_greater_then_20 = Product.objects.filter(unit_price__gt = 20)
    print(product_price_greater_then_20)
    querySet = Product.objects.filter(unit_price__range=(20,50))
    print(querySet)

    # filter through realtions
    productsInCollectionSet = Product.objects.filter(collection_id__gt=3)

    customer = Customer.objects.filter(email__icontains='.com')
    collection = Collection.objects.filter(featured_product_id = None)
    productsWithLowInventory = Product.objects.filter(inventory__lt=10)
    orders = Order.objects.filter(customer__id=1)

    # SQL query:
    # select count(*) from store_orderItem 
    # join store_product on store_orderItem.product_id = store_product.id 
    # join store_collection on store_product.collection_id = store_collection.id
    # where store_collection.id = 3;
    orderItems = OrderItem.objects.filter(product__collection__id=3)
    count = OrderItem.objects.filter(product__collection__id=3).count()


    return render(request, "hello.html", {"name":"Tina", "orderItems": list(orderItems), 'count':count})