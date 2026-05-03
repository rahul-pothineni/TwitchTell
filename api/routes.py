from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# from api.views.chat import ChatMessageViewSet  # add as you build them

router = DefaultRouter()
# router.register(r"chat", ChatMessageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("test/", views.dropdownMenuData),
]