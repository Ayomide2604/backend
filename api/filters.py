from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from .models import Product, Collection
from .serializers import ProductSerializer


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    collection = filters.CharFilter(
        field_name="collection__name", lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'collection']
