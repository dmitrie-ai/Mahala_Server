from django.urls import path
from django.contrib import admin
from django.conf import settings

from rest_framework import routers
from api import views as api_views
from django.conf.urls.static import static


router = routers.DefaultRouter()

urlpatterns = router.urls

urlpatterns += [
    path('admin/', admin.site.urls),
    path('register/', api_views.UserRegistrationView.as_view()),
    path('login/', api_views.LoginView.as_view()),
    path('logout/', api_views.LogoutView.as_view()),
    path('market/', api_views.MarketView.as_view()),
    path('main/', api_views.UserView.as_view()),
    path('inventory/add_item', api_views.AddItemView.as_view()),
    path('test/test1', api_views.TestView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.BASE_DIR)