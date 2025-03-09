from rest_framework import serializers
from .models import CustomUser, Enquiry, Seller, Buyer,User, Wishlist, Cart, CartProduct, Order, OrderItem, Product
from django.contrib.auth.models import User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'contact_number']

    def create(self, validated_data):
        # You can add password hashing logic here if needed
        user = User.objects.create(**validated_data)
        return user


class SellerRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    location = serializers.CharField(required=True)  # Ensure location is included
    pincode = serializers.CharField(required=True)   # Ensure pincode is included
    phone_number = serializers.CharField(required=True)  # Ensure phone_number is included
    email = serializers.CharField(required=True)
    class Meta:
        model = CustomUser  # Use CustomUser model
        fields = ['username', 'email', 'password', 'password2', 'location', 'pincode','phone_number']  # Only include fields from CustomUser

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match.")
         # Ensure that the email is unique
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email is already in use.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # Remove password2 from the validated data

        # Extract the additional fields for the Seller model
        location = validated_data.pop('location')
        pincode = validated_data.pop('pincode')
        phone_number = validated_data.pop('phone_number', None)

        # Create the user using CustomUser
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Create the seller profile associated with the user
        Seller.objects.create(
         user=user,
            location=location,
            pincode=pincode,
            phone_number=phone_number,
            email=validated_data['email']
        )

        return user


class BuyerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    email = serializers.EmailField(source="user.email")
    password = serializers.CharField(write_only=True, source="user.password")
    contact_number = serializers.CharField()

    class Meta:
        model = Buyer
        fields = ["id", "username", "email", "password", "contact_number"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        contact_number = validated_data.pop('contact_number', None)

        user = CustomUser.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"]
        )
        buyer = Buyer.objects.create(user=user, contact_number=contact_number)
        return buyer
# category
from .models import Product, Category

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['seller']



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'product']

class CartProductSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartProduct
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price()

class CartSerializer(serializers.ModelSerializer):
    cart_products = CartProductSerializer(many=True, read_only=True)
    total_cart_value = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'cart_products', 'total_cart_value']

    def get_total_cart_value(self, obj):
        return sum(item.total_price() for item in obj.cart_products.all())

class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price()

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status', 'order_items']


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = ['id', 'product', 'quantity', 'status', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['buyer'] = request.user
        return super().create(validated_data)
    
class EnquiryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = ['status']