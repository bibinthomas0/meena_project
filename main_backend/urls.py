from django.contrib import admin
from django.urls import path, include
from api.urls import api_router
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # Assuming 'api' is the name of your app
    path('', include(api_router.urls))
]
