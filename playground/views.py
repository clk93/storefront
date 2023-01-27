from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q, F, Count, Min, Max, Avg, Aggregate, Sum

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
        pass

    product1 = Product.objects.get(pk=1)

    # if a product does not exist by id, exception will be thrown
    try:
        product_not_exist = Product.objects.get(pk=0)
    except ObjectDoesNotExist:
        pass

    # but filter with first() method will deliver a non, if product does not
    # exist, instead of throwing exception
    product_none = Product.objects.filter(pk=1).first()

    # check existence -> boolean
    exists = Product.objects.filter(pk=42).exists()

    # filter
    product_price_greater_then_20 = Product.objects.filter(unit_price__gt=20)
    querySet = Product.objects.filter(unit_price__range=(20, 50))

    # filter through realtions
    productsInCollectionSet = Product.objects.filter(collection_id__gt=3)

    customer = Customer.objects.filter(email__icontains='.com')
    collection = Collection.objects.filter(featured_product_id=None)
    productsWithLowInventory = Product.objects.filter(inventory__lt=10)
    orders = Order.objects.filter(customer__id=1)

    # SQL query:
    # select count(*) from store_orderItem
    # join store_product on store_orderItem.product_id = store_product.id
    # join store_collection on store_product.collection_id = store_collection.id
    # where store_collection.id = 3;
    orderItems = OrderItem.objects.filter(product__collection__id=3)
    count = OrderItem.objects.filter(product__collection__id=3).count()

    # query expressions with Query Object unit_price > 10 OR NOT inventory <=2
    Product.objects.filter(Q(unit_price__gt=10) | ~ Q(inventory__lte=3))

    # field reference
    Product.objects.filter(unit_price=F('inventory'))

    # sort unit_price asc and title desc and limit
    products = Product.objects.order_by('unit_price', '-title')[:25]
    product_count = products.count()

    # paging
    products_Paginated = Product.objects.values(
        'title').order_by('unit_price', '-title')[:25]
    products_page_1 = Paginator(products_Paginated, 5).page(1)
    count = products_page_1.object_list.count

    # select products that have been ordered and sort them by title
    products_without_duplicates = Product.objects.filter(
        id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

    # select related (1:1) -> SELECT ••• FROM `store_product` INNER JOIN `store_collection` ON (`store_product`.`collection_id` = `store_collection`.`id`)
    products_with_collection = Product.objects.select_related(
        'collection').all()

    # prefetch related (1:n) ->
    promotions = Product.objects.prefetch_related('promotions').all()

    # Get the last 5 orders with their customer and items (incl product)
    # select * from store_orderitem as oi
    # join store_order as o on o.id = oi.id
    # join store_customer as c on o.customer_id = c.id
    # join store_product as p on oi.product_id = p.id
    # order by placed_at limit 5;
    # Remember: Django is creating the reverse relationship for foreign key related objects
    # default name orderitem_set for order in orderitem
    ordersWithCustomerItemsAndProduct = Order.objects.select_related(
        'customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    # return render(request, "hello.html", {"name":"Tina", "products": products_with_collection, 'product_count': products_without_duplicates.count()})

    #Aggregates don't return a query set, they return a dictonary
    product_aggregate = Product.objects.filter(collection__id=3).aggregate(count=Count('id'), minPrice=Min('unit_price'))
    order_aggregate = Order.objects.aggregate(count=Count('id'))

    '''
    Write code to answer the following questions:
    •How many orders do we have?
    •How many units of product 1 have we sold?
    •How many orders has customer 1 placed?
    •What is the min, max and average price of the products in collection 3?
    '''
    order_count_aggregate = Order.objects.aggregate(count=Count('id'))
    product_1_soldUnits = OrderItem.objects.filter(product__id=1).aggregate(sum=Sum('quantity'))
    orders_placedBy_Customer1= Order.objects.filter(customer__id=1).aggregate(count=Count('id'))
    products_collection3 = Product.objects.filter(collection__id=3).aggregate(min=Min('unit_price'), max=Max('unit_price'), avg=Avg('unit_price'))

    return render(request, "hello.html", {"name": "Tina", "orders": ordersWithCustomerItemsAndProduct, 'oder_count': ordersWithCustomerItemsAndProduct.count(), 'order_aggregate': products_collection3})
