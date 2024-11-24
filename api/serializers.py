from rest_framework import serializers
from .models import Product, Collection, Cart, CartItem


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ['id', 'name', 'products_count']

    def get_products_count(self, obj):
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'collection', 'price']



from rest_framework import serializers

class CartSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    cart_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'total_price', 'cart_items']

    def get_total_price(self, obj):
        return obj.total_price()

    def get_cart_items(self, obj):
        from .serializers import CartItemSerializer
        return CartItemSerializer(obj.cart_items.all(), many=True).data

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.ReadOnlyField(source="product.price")

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity']
