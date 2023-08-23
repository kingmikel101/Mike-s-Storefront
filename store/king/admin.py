from django.contrib import admin
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'
    
    def lookups(self, request, model_admin):
        return [
            ('<10', 'low')
        ]
        
    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__it=10)
        
@admin.register(models.Product)
class productAdmin(admin.ModelAdmin):
     autocomplete_fields = ['collection']
     prepopulated_fields = {
         'slug': ['title']
     }
     actions = ['clear_inventory']
     list_display = ['title', 'unit_price',
                     'inventory',]
     list_editable = ['unit_price']
     list_filter = ['collection', 'last_update', InventoryFilter]
     list_per_page = 10
     list_select_related = ['collection']
     
     def collecton_title(self, product):
         return product.collection.title

@admin.display(ordering='inventory',)
def inventory_status(self, product):
    if product.inventory < 10:
       return 'low'
    return 'ok'
@admin.action(description='Clear inventory')
def clear_inventory(self, request, queryset):
    updated_count = queryset.update(inventory=0)
    self.message_user(
        request,
        f'{updated_count} product were succesfully updated.'
    )



@admin.register(models.Collection)
class collectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']
    
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
            reverse('admin:king_product_changelist')
            + '?' 
            + urlencode({
                'collection__id': str (collection.id)
            }) )
        return format_html('<a href="{}">{}</a>', url, collection.products_count)
        
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )

class orderItemInline(admin.StackedInline):
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [orderItemInline]
    list_display = ['id', 'placed_at', 'customer']


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    list_per_page = 10
    oredering = ['first_name__istartswith', 'last_name__istartswith']
    search_fields = ['first_name', 'last_name']




