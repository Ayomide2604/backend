from rest_framework import serializers
from .models import Product, Collection, Cart, CartItem, Order, OrderItem


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
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        # Calculate total price for each cart item (product price * quantity)
        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'cart_items', 'created_at', 'total_price']

    def get_total_price(self, obj):
        # Calculate the total price for the entire cart
        return obj.total_price()


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'payment_status', 'order_items']

    def get_order_items(self, obj):
        from .serializers import OrderItemSerializer
        return OrderItemSerializer(obj.order_items.all(), many=True).data


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.ReadOnlyField(source="product.price")

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity']
