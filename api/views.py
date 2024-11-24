from .serializers import CartSerializer
from .models import Cart
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from django.shortcuts import render
from .models import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from . serializers import *


# Create your views here.


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [AllowAny]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    # Custom action to add product to cart
    @action(detail=True, methods=['post', 'get'])
    def add_to_cart(self, request, pk=None):
        product = self.get_object()
        user = request.user

        # Get the user's cart or create a new one if it doesn't exist
        cart, created = Cart.objects.get_or_create(user=user)

        # Check if the product is already in the cart
        cart_item, cart_item_created = CartItem.objects.get_or_create(
            cart=cart, product=product
        )

        if not cart_item_created:
            # If the cart item already exists, update the quantity
            cart_item.quantity += 1
            cart_item.save()

        # Calculate total price of cart items (optional, if needed for the response)
        total_price = cart.total_price()

        # Serialize and return the updated cart
        cart_serializer = CartSerializer(cart)
        return Response({
            'message': 'Product added to cart',
            'cart': cart_serializer.data,
            'total_price': total_price
        }, status=status.HTTP_200_OK)


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer  # Specify the serializer to be used

    def get_queryset(self):
        # Ensures a user can only have one active cart
        return Cart.objects.filter(user=self.request.user)

    def list(self, request):
        # Check if the user has an existing cart
        cart = Cart.objects.filter(user=request.user).first()

        # If a cart exists, return it, otherwise create a new one and return that
        if cart:
            serializer = CartSerializer(cart)
            return Response(serializer.data)

        # If no cart exists, create a new one and return the new cart details
        cart = Cart.objects.create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        # Ensure a cart does not exist already before creating one
        if Cart.objects.filter(user=request.user).exists():
            return Response({"message": "Cart already exists. You can only have one cart."},
                            status=status.HTTP_400_BAD_REQUEST)

        # If no cart exists, create a new one
        cart = Cart.objects.create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        # Only allow deleting the user's cart
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "No cart found to delete"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'get'], url_path='checkout')
    def checkout(self, request):
        # Retrieve the user's cart
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return Response({"error": "No active cart found."}, status=status.HTTP_400_BAD_REQUEST)

        # Create an Order
        order = Order.objects.create(
            user=request.user, payment_status="PENDING")

        # Convert CartItems to OrderItems
        for cart_item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )

        # Delete the cart after order is created
        cart.delete()

        # Serialize the order and return the response
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()  # Queryset to use for the viewset
    serializer_class = OrderSerializer  # Specify the serializer to use
    # Only authenticated users can access this viewset
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return Response({"error": "No active cart found."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user, payment_status="PENDING")
        for cart_item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )
        cart.delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
