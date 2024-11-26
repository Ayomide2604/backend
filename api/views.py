from .serializers import CartSerializer
from .models import Cart
from rest_framework import viewsets, status
from django.shortcuts import render
from .models import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from . serializers import *
from .filters import ProductFilter
from rest_framework.exceptions import NotFound


# Create your views here.


# CollectionViewSet - Allow anyone to view collections
class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    search_fields = ['name']
    ordering_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only staff and superusers can create, update, or delete
            return [IsAdminUser()]
        return [AllowAny()]  # Anyone can view products

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


# ProductViewSet - Allow anyone to view products, only authenticated users can add to cart
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ['name', 'collection__name']
    ordering_fields = ['price', 'name', 'date_created']
    ordering = ['name']  # default ordering

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only staff and superusers can create, update, or delete
            return [IsAdminUser()]
        return [AllowAny()]  # Anyone can view products

    # Custom action to add product to cart - Check if user is authenticated

    @action(detail=True, methods=['post', 'get'], permission_classes=[AllowAny])
    def add_to_cart(self, request, pk=None):
        product = self.get_object()
        user = request.user if request.user.is_authenticated else None

        # If the user is authenticated, get or create their cart, else work with anonymous cart
        if user:
            cart, created = Cart.objects.get_or_create(user=user)
        else:
            # Handle anonymous cart here if needed (you can use session or IP-based storage)
            return Response({"error": "Please login to add products to your cart."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the product is already in the cart
        cart_item, cart_item_created = CartItem.objects.get_or_create(
            cart=cart, product=product
        )

        if not cart_item_created:
            # If the cart item already exists, update the quantity
            cart_item.quantity += 1
            cart_item.save()

        # Serialize and return the updated cart
        cart_serializer = CartSerializer(cart)
        # Assuming a total_price method is implemented on Cart
        total_price = cart.total_price()
        return Response({
            'message': 'Product added to cart',
            'cart': cart_serializer.data,
            'total_price': total_price
        }, status=status.HTTP_200_OK)

    # Custom action to add product images
    @action(detail=True, methods=['post', 'get'], permission_classes=[IsAdminUser])
    def add_image(self, request, pk=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only staff and superusers can create/update/delete
            self.permission_classes = [IsAdminUser]
        else:
            # Other actions like view are accessible by any user
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        # Filter the images for the product based on 'product_pk'
        product_id = self.kwargs.get('product_pk')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound("Product not found.")
        return ProductImage.objects.filter(product=product)

    def perform_create(self, serializer):
        # Associate the product with the image being created
        product = Product.objects.get(id=self.kwargs['product_pk'])
        serializer.save(product=product)


# CartViewSet - Only authenticated users can place an order
class CartViewSet(viewsets.ModelViewSet):
    # Only authenticated users can interact with cart
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        # Ensure the user can only access their own cart
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
            return Response(
                {"message": "Cart already exists. You can only have one cart."},
                status=status.HTTP_400_BAD_REQUEST
            )

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

    # Checkout action, only available to authenticated users
    @action(detail=False, methods=['post', 'get'], url_path='checkout')
    def checkout(self, request):
        # Retrieve the user's cart
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return Response({"error": "No active cart found."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the cart contains any items
        cart_items = cart.cart_items.all()
        if not cart_items.exists():
            return Response({"error": "Cannot proceed to checkout. Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Create an Order
        order = Order.objects.create(
            user=request.user,
            payment_status="PENDING"
        )

        # Convert CartItems to OrderItems
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )

        # Delete the cart after order is created
        cart.delete()

        # Serialize the order and return the response
        serializer = OrderSerializer(order)
        return Response({
            "message": "Order created successfully. Proceed to payment.",
            "order": serializer.data
        }, status=status.HTTP_201_CREATED)


class CartItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

    @action(detail=True, methods=['patch', 'get'], url_path='increment')
    def increment(self, request, pk=None, cart_pk=None):
        try:
            cart_item = self.get_object()
            cart_item.quantity += 1
            cart_item.save()
            return Response({
                'message': 'Item quantity incremented successfully',
                'item': CartItemSerializer(cart_item).data
            }, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch', 'get'], url_path='decrement')
    def decrement(self, request, pk=None, cart_pk=None):
        try:
            cart_item = self.get_object()
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return Response({
                    'message': 'Item quantity decremented successfully',
                    'item': CartItemSerializer(cart_item).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Cannot decrement below 1'
                }, status=status.HTTP_400_BAD_REQUEST)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    # Only authenticated users can access this viewset
    permission_classes = [IsAuthenticated]
    ordering = ['created_at']

    def get_permissions(self):
        if self.action in ['create']:
            # Only authenticated users can create orders
            return [IsAuthenticated()]
        elif self.action in ['list', 'retrieve']:
            # Admin users can see all orders
            if self.request.user.is_staff:
                return [IsAdminUser()]
            # Non-admin users can only view their own orders
            return [IsAuthenticated()]
        return [IsAuthenticated()]  # Default permission for other actions

    def get_queryset(self):
        """
        Custom queryset for viewing orders:
        - Admin can see all orders.
        - Authenticated users can only see their own orders.
        """
        if self.request.user.is_staff:
            return Order.objects.all()  # Admin users can see all orders
        # Users can only see their own orders
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "You must be logged in to create an order."},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Check if the user has an active cart
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return Response({"error": "No active cart found."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order
        order = Order.objects.create(
            user=request.user, payment_status="PENDING")

        # Create order items from the cart
        for cart_item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )

        # Once the order is created, delete the cart
        cart.delete()

        # Serialize and return the created order
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
