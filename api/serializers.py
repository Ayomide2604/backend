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
        fields = ['id', 'image', ]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'collection', 'price', 'images']


class SimpleProductSerializer(serializers.ModelSerializer):
    collection = CollectionSerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'collection']


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
    product = SimpleProductSerializer(read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price', 'product_image']

    def get_total_price(self, obj):
        # Calculate total price for each cart item (product price * quantity)
        return obj.product.price * obj.quantity

    def get_product_image(self, obj):
        # Assuming product has a related field 'images' and we fetch the first image
        if obj.product.images.exists():
            first_image = obj.product.images.first().image.url
            # Append the localhost API URL to the image path
            return f"http://127.0.0.1:8000{first_image}"
        # Fallback if no image exists
        return None


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
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'payment_status',
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
