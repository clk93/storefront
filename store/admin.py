from typing import Any, Optional, Tuple, List
from urllib.parse import urlencode
from django.contrib import admin
from django.db.models import QuerySet, Count
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from . import models

admin.site.register(models.Address)

INVENTORY_LIMIT = 10
INVENTORY_LOW = 'Low'
INVENTORY_OK = 'OK'

# custom filter
class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'
    lowParam = '<' + str(INVENTORY_LIMIT)
    okParam = '>=' + str(INVENTORY_LIMIT)

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return [
            (self.lowParam, INVENTORY_LOW),
            (self.okParam, INVENTORY_OK)
        ]
    
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> Optional[QuerySet[Any]]:
        if self.value() == self.lowParam:
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']
    prepopulated_fields= {
        'slug': ['title',]
        }
    autocomplete_fields=['collection']
    search_fields=['title']
    list_display = ['title', 'unit_price',
                    'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection', 'last_update', InventoryFilter]

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < INVENTORY_LIMIT:
            return INVENTORY_LOW
        return INVENTORY_OK
    
    # create custom action
    @admin.action(description='clear inventory')
    def clear_inventory(self, request: HttpRequest, querySet: QuerySet):
        updated_count = querySet.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated'
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'membership', 'orders_count']
    list_editable = ['membership']
    list_per_page = 10
    # use lookup types for better controle; i (of startswith) means case insensitive
    search_fields=['first_name__istartswith', 'last_name__istartswith', 'email__istartswith']
    ordering = ['first_name', 'last_name']

    @admin.display(ordering='orders_count')
    def orders_count(self, customer):
        url = (reverse('admin:store_order_changelist')
        + '?'
        + urlencode({
            'customer__id': str(customer.id)
        })
        )
        return format_html('<a href="{}">{}</a>', url, customer.orders_count)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            orders_count = Count('order')
        )

class OrderItemInline(admin.TabularInline):
    autocomplete_fields=['product']
    model = models.OrderItem
    extra = 0

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields= ['customer']
    ordering = ['placed_at']
    inlines = [OrderItemInline]
    search_fields=['placed_at']
    list_display = ['placed_at', 'payment_status',
                    'customer', 'customer_email']
    list_per_page = 10
    list_select_related = ['customer']

    def customer_email(self, order):
        return order.customer.email

    customer_email.admin_order_field = 'customer__email'
    customer_email.short_description = "Customer Mail"


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    # products_count is not a given field of Collection -> needs to be calculated
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        # template: app_model_page
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            })
        )
        return format_html('<a href="{}">{}</a>', url, collection.products_count)

    # overriding the base query set
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )
