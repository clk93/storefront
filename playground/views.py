from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction, connection
from django.db.models import Q, F, Count, Min, Max, Avg, Aggregate, Sum, Value, Func, ExpressionWrapper, DecimalField, BooleanField
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType

from store.models import Product, Customer, Collection, Order, OrderItem, Cart, CartItem
from tag.models import TagItem


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

    getAndFilterDBObjects()

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
    ordersWithCustomerItemsAndProduct = Order.objects\
        .select_related('customer')\
        .prefetch_related('orderitem_set__product')\
        .order_by('-placed_at')[:5]
    # return render(request, "hello.html", {"name":"Tina", "products": products_with_collection, 'product_count': products_without_duplicates.count()})

    #Aggregates don't return a query set, they return a dictonary
    useAggregates()
   
    # Annotation: bring a new field to object
    # Annotation needs a Expression (like Aggregate, F, Func, Value)
    useAnnotations()

    # Query generic relationships using custom manager
    TagItem.objects.get_tags_for(Product, 1)

    creatUpdateAndDeleteOperations()

    # Work with transactions as decorator
    transactional_create_order()

    # transaction with context manager
    transaction_context_manager()

    # write raw SQL, if queries get too complex
    writeRawSql()

    return render(request, "hello.html", {"name": "Tina", "orders": ordersWithCustomerItemsAndProduct, 'oder_count': ordersWithCustomerItemsAndProduct.count()})

def getAndFilterDBObjects():
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

def useAggregates():
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

def useAnnotations():
    new_customer = Customer.objects.annotate(new_customer=Value(True))
    new_customer_id = Customer.objects.annotate(new_id= F('id') + 1)
    
    # calling DB functions
    customer_fullname = Customer.objects.annotate(full_name=Func(
        # CONCAT
        F('first_name'), Value(' '), F('last_name'), function='CONCAT'
        ))
    # Django DB functions: shorthand
    customer_fullname_short = Customer.objects.annotate(
        full_name=Concat('first_name', Value(' '), 'last_name')
    )

    #grouping date
    countOrder = Customer.objects.annotate(
        # caution, cause reverse relation field should have the name 'order-set' but
        # for some reasons an FieldError is thrown, cause unknown field
        order_count = Count('order')
    )

    # expression wrapper
    discountPrice = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
    orderWithDiscountPrice = Product.objects.annotate(
        discount_price = discountPrice
    )

    """
    practice:
     •Customers with their last order ID
     •Collections and count of their products 
     •Customers with more than 5 orders
     •Customers and the total amount they’ve spent
     •Top 5 best-selling products and their total sales
    """
    customer_last_order_id = Customer.objects.annotate(
        last_order_id = Max('order__id')
    )

    collection_count_product = Collection.objects.annotate(
        count_products = Count('product')
    )
    
    customer_with_more_than_5_orders = Customer.objects.annotate(
        orders_count = Count('order')
    ).filter(orders_count__gt=5)

    customer_with_total_spent_amount = Customer.objects.annotate(
        amount_spent = Sum(F('order__orderitem__quantity') * F('order__orderitem__unit_price'))
    )

    top_products = Product.objects.annotate(
        total_sales = Sum(F('orderitem__quantity') * F('orderitem__unit_price'))
    ).order_by('-total_sales')[0:5]


def creatUpdateAndDeleteOperations():
      # Creationg an object
    newCollection1 = Collection()
    newCollection1.title = 'Video Games'
    newCollection1.featured_product = Product(pk=1)
    newCollection1.save()
    # Alternative: 
    Collection.objects.create(title='Music Disc', featured_product_id=2)

    # Updating an object
    updateCollection1 = Collection(pk=1)
    updateCollection1.title = 'Video Games 2'
    updateCollection1.featured_product = None
    updateCollection1.save()
    # Attention: if e.g. title is not set, cause update is not necessary for this field,
    # Django will overwrite it and set title to empty field -> read fresh from the db and
    # update fields, which should be changed
    updateCollection2 = Collection.objects.get(pk=1)
    updateCollection2.featured_product = None
    updateCollection2.save()
    #Alternative:
    Collection.objects.filter(pk=3).update(featured_product=None)

    # Deleting an Object
    deleteCollection = Collection(pk=11)
    deleteCollection.delete()
    # Alternative
    Collection.objects.filter(id__gt=7).delete()

    """
    Practice:
    •Create a shopping cart with an item
    •Update the quantity of an item in a shopping cart
    •Remove a shopping cart with its items
    """
    newCart = Cart.objects.create()
    newCartItem = CartItem()
    newCartItem.cart = newCart
    newCartItem.product = Product(pk=1)
    newCartItem.quantity = 5
    newCartItem.save()

    CartItem.objects.filter(pk=1).update(quantity=7)

    CartItem.objects.filter(pk=2).delete()
    # also with delete on cascade deletion of Cart will also delete CartItem
    Cart.objects.filter(pk=5).delete()


@transaction.atomic()
def transactional_create_order():
    order = Order()
    order.customer = Customer(pk=1)
    order.save()

    orderItem = OrderItem()
    orderItem.order = order
    orderItem.product = Product(pk=4)
    orderItem.quantity = 42
    orderItem.unit_price = 5
    orderItem.save()

def transaction_context_manager():
    # .... code....

    with transaction.atomic():
        order = Order()
        order.customer = Customer(pk=2)
        order.save()

        orderItem = OrderItem()
        orderItem.order = order
        orderItem.product = Product(pk=5)
        orderItem.quantity = 42
        orderItem.unit_price = 7
        orderItem.save()

def writeRawSql():
    # option 1:
    querySetRaw = Product.objects.raw('SELECT * FROM store_product') 

    # option 2:
    # with an exception also cursor get's closed; otherwise use try finally block to close cursor
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM store_product')
       # cursor.callproc('get_customers', [1,2])

