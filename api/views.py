import random
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Enquiry,CustomUser
from .serializers import EnquirySerializer, EnquiryUpdateSerializer, OrderItemSerializer, OrderItemStatusUpdateSerializer, UserRegistrationSerializer
from rest_framework import viewsets, permissions,generics
from .models import Product
from .serializers import ProductSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Wishlist, Cart, CartProduct, Order, OrderItem, Product
from .serializers import WishlistSerializer, CartSerializer, OrderSerializer
from rest_framework.decorators import api_view, permission_classes
from .models import Category
from .serializers import CategorySerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers, status
from .order_serializers import OrderItemSerializer_2, OrderSerializer_2
from django.core.mail import send_mail

from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserDetailsSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    return Response({"message": "Token is valid!"}, status=200)

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class LoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = CustomUser.objects.filter(username=username).first()
            if user.is_active == False:
                return Response({"error": "You are blocked from this site. Please contact administrator"}, status=status.HTTP_401_UNAUTHORIZED)
            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                user_data = UserRegistrationSerializer(user).data
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': 'admin' if user.is_superuser else 'seller' if user.is_seller else 'buyer',
                    'user_data': user_data
                }, status=status.HTTP_200_OK)

            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListUsersAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_type):
        if user_type == 'seller':
            users = CustomUser.objects.filter(is_seller=True)
        elif user_type == 'buyer':
            users = CustomUser.objects.filter(is_buyer=True)
        else:
            return Response({"error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserRegistrationSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UserRegistrationSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteUserAPIView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            if not user.is_active:
                return Response({"message": "User deactivated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User Activated successfully"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


    

class CategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_list_create(request):
    if request.method == 'GET':
        if request.user.is_buyer:
            selected_pincodes = request.user.selected_pincodes.split(',')  # Assuming this is a list of pincodes
            products = Product.objects.filter(seller__pincode__in=selected_pincodes)
        else:
            products = Product.objects.filter(seller=request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Debugging: Log validation errors
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
        cart = Cart.objects.filter(user=self.request.user).order_by('-created_at').first()
        if not cart:
            cart = Cart.objects.create(user=self.request.user)
        return cart 

class CartUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=self.request.user).order_by('-created_at').first()
        if not cart:
            cart = Cart.objects.create(user=self.request.user)
        product = get_object_or_404(Product, id=request.data.get("product"))
        quantity = request.data.get("quantity", 1)

        if product.stock < quantity:
            return Response({"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)

        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_product.quantity = quantity
        cart_product.save()

        return Response({"message": "Product added/updated in cart"}, status=status.HTTP_200_OK)

class CartDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        data = Cart.objects.filter(user=self.request.user).first()
        if data:
            cart = data
        else:
            cart = Cart.objects.create(user=self.request.user)
        product = get_object_or_404(Product, id=request.data.get("product"))

        cart_product = get_object_or_404(CartProduct, cart=cart, product=product)
        cart_product.delete()

        return Response({"message": "Product removed from cart"}, status=status.HTTP_200_OK)

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=self.request.user).order_by('-created_at').first()
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

class OrderItemStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_item_id):
        try:
            order_item = OrderItem.objects.get(id=order_item_id)
        except OrderItem.DoesNotExist:
            return Response({"error": "Order item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderItemStatusUpdateSerializer(order_item, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            user_email = order_item.order.user.email
            if request.data['status'] == 'Shipped':
                message = f"Good news! Your item {order_item.product.title} with the total price of {float(order_item.total_price())} has been Shipped. "
            elif request.data['status'] == 'Out For Delivery':
                message = f"Order is in your door step! Your item {order_item.product.title} with the total price of {float(order_item.total_price())} has been for out for delivery. Please make sure to available in the shop"
            elif request.data['status'] == 'Delivered':
                message = f"Order delivered! Your item {order_item.product.title} with the total price of {float(order_item.total_price())} has been delivered. Happy to shop with you"
            mail =  send_order_status_email(self,message,user_email)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnquiryViewSet(viewsets.ModelViewSet):
    serializer_class = EnquirySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_buyer == True:
            return Enquiry.objects.filter(buyer=user)
        elif user.is_seller == True:
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
        # enquiry.product.stock -= enquiry.quantity
        enquiry.product.save()


class SellerOrdersView(generics.ListAPIView):
    serializer_class = OrderItemSerializer_2
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        seller = self.request.user
        return OrderItem.objects.filter(product__seller=seller)


class BuyerOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer_2
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class UpdateOrderItemStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, order_item_id):
        order_item = OrderItem.objects.get(id=order_item_id) 
        new_status = request.data.get("status")
        
        if order_item.status not in ["Pending"] and new_status == "Cancelled":
            return Response({"error": "Item cant be cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        
        order_item.status = new_status
        order_item.save()
        
        return Response({"message": "Order item status updated successfully"}, status=status.HTTP_200_OK)
    


def send_order_status_email(self,message,user_email):
    status = send_mail(
        'order status',
        message,
        'zorpia.Ind@gmail.com', 
        [user_email],  
        fail_silently=False,
    )

    return status





class UserDetailsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailsSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserDetailsSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User details updated", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellerPincodeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = CustomUser.objects.filter(is_seller=True).values_list('pincode',flat=True)
        return Response(data, status=status.HTTP_200_OK)
    


from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import HelpAndSupport
from .serializers import HelpAndSupportSerializer, HelpAndSupportReplySerializer

class HelpAndSupportCreateView(generics.CreateAPIView):
    serializer_class = HelpAndSupportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Comment created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "Failed to create comment.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class HelpAndSupportListView(generics.ListAPIView):
    serializer_class = HelpAndSupportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            queryset = HelpAndSupport.objects.all().order_by('-created_on')
        else:
            queryset = HelpAndSupport.objects.filter(user=user).order_by('-created_on')

        serializer = self.get_serializer(queryset, many=True) 
        return Response({
            "message": "Comments fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class HelpAndSupportReplyView(generics.UpdateAPIView):
    queryset = HelpAndSupport.objects.all()
    serializer_class = HelpAndSupportReplySerializer
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Reply added successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "Failed to add reply.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except HelpAndSupport.DoesNotExist:
            return Response({
                "message": "Comment not found."
            }, status=status.HTTP_404_NOT_FOUND)

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