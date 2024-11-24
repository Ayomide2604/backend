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


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer  # Specify the serializer to be used

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


class CartItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
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
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
