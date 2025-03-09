from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Enquiry, Seller, Buyer,CustomUser
from .serializers import EnquirySerializer, EnquiryUpdateSerializer, SellerRegisterSerializer, BuyerSerializer  # Removed RegisterSerializer
from rest_framework import viewsets, permissions,generics
from rest_framework.permissions import BasePermission
from .models import Product
from .serializers import ProductSerializer
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Wishlist, Cart, CartProduct, Order, OrderItem, Product
from .serializers import WishlistSerializer, CartSerializer, OrderSerializer
from rest_framework.decorators import api_view, permission_classes
from .models import Category
from .serializers import CategorySerializer


class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ----------------- Seller Registration -----------------
class SellerRegisterView(APIView):
    def post(self, request):
        serializer = SellerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Seller registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------- Buyer Registration -----------------
class BuyerRegisterView(APIView):
    def post(self, request):
        serializer = BuyerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Buyer registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------- User Login -----------------
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"message": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({"access_token": str(refresh.access_token), "refresh_token": str(refresh)}, status=status.HTTP_200_OK)

        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

# ----------------- Seller Login -----------------
class SellerLoginView(APIView):
    def post(self, request):
        print(request.data)
        username = request.data.get('username')
        password = request.data.get('password')
      
        # Ensure both username and password are provided
        if not username or not password:
            return Response({"message": "username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user
        user = authenticate(username=username, password=password)
        print(user)
        if user:
            try:
                # Attempt to retrieve the seller profile associated with the user
                seller = Seller.objects.get(user=user)
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                data = {
                    "message": "Login successful.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "seller_details": {
                        "username": user.username,
                        "email": user.email,
                        "location": seller.location,
                        "pincode": seller.pincode,
                        "district": seller.district,
                        "phone_number": seller.phone_number  # Include phone_number
                    },
                    "product_creation_link": "/seller/products/create/"  # Link to product creation page
                }
                return Response(data=data, status=status.HTTP_200_OK)

            except Seller.DoesNotExist:
                return Response({"message": "No seller profile found."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

# ----------------- Buyer Login -----------------
class BuyerLoginView(APIView):
    def post(self, request):
        print(request.data)
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"message": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        print(user)
        if user:
            try:
                buyer = Buyer.objects.get(user=user)
                print(buyer)
                refresh = RefreshToken.for_user(user)
                data={
                    "message": "Login successful.",
                    "access": str(refresh.access_token),
                    "buyer_details": {
                        "username": user.username,
                        "email": user.email,
                    }
                }
                return Response(data=data, status=status.HTTP_200_OK)
            except Buyer.DoesNotExist:
                return Response({"message": "No buyer profile found."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_list_create(request):
    """List all products of the authenticated seller or create a new product."""
    if request.method == 'GET':
        products = Product.objects.filter(seller=request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, pk):
    """Retrieve, update, or delete a product by ID (only if owned by seller)."""
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        serializer = ProductSerializer(product, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

class WishlistView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=request.data.get("product"))
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if created:
            return Response({"message": "Product added to wishlist"}, status=status.HTTP_201_CREATED)
        else:
            wishlist_item.delete()
            return Response({"message": "Product removed from wishlist"}, status=status.HTTP_200_OK)

class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

class CartUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=request.data.get("product"))
        quantity = request.data.get("quantity", 1)

        if product.stock < quantity:
            return Response({"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)

        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_product.quantity += quantity
        cart_product.save()

        return Response({"message": "Product added/updated in cart"}, status=status.HTTP_200_OK)

class CartDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        product = get_object_or_404(Product, id=request.data.get("product"))

        cart_product = get_object_or_404(CartProduct, cart=cart, product=product)
        cart_product.delete()

        return Response({"message": "Product removed from cart"}, status=status.HTTP_200_OK)

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.cart_products.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user)

        for cart_product in cart.cart_products.all():
            if cart_product.product.stock < cart_product.quantity:
                return Response({"error": f"Not enough stock for {cart_product.product.title}"}, status=status.HTTP_400_BAD_REQUEST)

            cart_product.product.stock -= cart_product.quantity
            cart_product.product.save()

            OrderItem.objects.create(order=order, product=cart_product.product, quantity=cart_product.quantity)

        cart.cart_products.all().delete()

        return Response({"message": "Order created successfully"}, status=status.HTTP_201_CREATED)

class OrderCancelView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs["pk"], user=request.user)
        if order.status != "Pending":
            return Response({"error": "Only pending orders can be cancelled"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = "Cancelled"
        order.save()
        return Response({"message": "Order cancelled"}, status=status.HTTP_200_OK)

class EnquiryViewSet(viewsets.ModelViewSet):
    serializer_class = EnquirySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'buyer_profile'):
            return Enquiry.objects.filter(buyer=user)
        elif hasattr(user, 'seller_profile'):
            return Enquiry.objects.filter(product__seller=user)
        return Enquiry.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        enquiry = serializer.save()
        return Response(EnquirySerializer(enquiry).data, status=status.HTTP_201_CREATED)
    

class EnquiryStatusUpdateView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def update(self, request, pk=None):
        try:
            enquiry = Enquiry.objects.get(pk=pk, product__seller=request.user)
        except Enquiry.DoesNotExist:
            return Response({"error": "Enquiry not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnquiryUpdateSerializer(enquiry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if enquiry.status == "Accepted":
                self.create_order(enquiry)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_order(self, enquiry):
        order = Order.objects.create(user=enquiry.buyer)
        OrderItem.objects.create(order=order, product=enquiry.product, quantity=enquiry.quantity)
        enquiry.product.stock -= enquiry.quantity
        enquiry.product.save()