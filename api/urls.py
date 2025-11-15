from django.urls import path
from .views import (
    RegisterView,
    DojoClassListCreateView,
    DojoClassDetailView,
    EnrollmentListCreateView,
    EnrollmentDetailView,
    PaymentListCreateView,
    PaymentDetailView,
    CustomTokenObtainPairView,
    admin_stats
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('admin/stats/', admin_stats, name='admin-stats'),
    
    # Class endpoints 
    path('classes/', DojoClassListCreateView.as_view(), name='class_list_create'),
    path('classes/<int:pk>/', DojoClassDetailView.as_view(), name='class_detail'),

    # Enrollments endpoint 
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment_list_create'),
    path('enrollments/<int:pk>/', EnrollmentDetailView.as_view(), name='enrollment_detail'),

    # Payment endpoints 
    path('payments/', PaymentListCreateView.as_view(), name='payment_list_create'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
]
