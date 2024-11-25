from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import *


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ['id', 'name', 'products_count']

    def get_products_count(self, obj):
        return obj.products.count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'collection', 'price', 'images']


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
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'payment_status',
                  'order_items', 'total_price']

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.order_items.all(), many=True).data

    def get_total_price(self, obj):
        # Calculate total price for the order by summing up the total price of all order items
        return sum(item.product.price * item.quantity for item in obj.order_items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.ReadOnlyField(source="product.price")
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name',
                  'product_price', 'quantity', 'total_price']

    def get_total_price(self, obj):
        # Calculate total price for each order item
        return obj.product.price * obj.quantity


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['name', 'bio', 'avatar', 'phone', 'address']


class CustomUserSerializer(BaseUserSerializer):
    profile = ProfileSerializer()

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('profile',)

    def update(self, instance, validated_data):
        # Handle profile update
        profile_data = validated_data.pop('profile', None)
        if profile_data:
            profile, created = Profile.objects.get_or_create(user=instance)
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.save()
        return super().update(instance, validated_data)
