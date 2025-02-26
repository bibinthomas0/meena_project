from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
class CustomUser(AbstractUser):
    location = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords!
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
# Seller model
class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seller_profile")
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6, default="000000")
    district = models.CharField(max_length=255, default="Unknown District")
    email = models.EmailField(unique=True)    

    def __str__(self):
        return self.user.username

class Buyer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buyer_profile")  # Store hashed passwords!
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username


# {category}
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
   
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=False, blank=False ,default='products/default_image.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_products")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Cancelled", "Cancelled"), ("Completed", "Completed")], default="Pending")

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def total_price(self):
        return self.product.price * self.quantity
