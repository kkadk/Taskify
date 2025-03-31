from .views import TaskViewSet
from rest_framework import routers
from django.urls import path, include
from .views import RegisterView, VerifyEmailView

router = routers.DefaultRouter()
router.register('taskm', TaskViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path ('register/', RegisterView.as_view(), name='register'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
]
