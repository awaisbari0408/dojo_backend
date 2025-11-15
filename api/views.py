from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .models import User, DojoClass, Enrollment, Payment
from .serializers import UserSerializer, DojoClassSerializer, EnrollmentSerializer, PaymentSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Public: register new user
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# Classes: list & create (admin/instructor create)
class DojoClassListCreateView(generics.ListCreateAPIView):
    queryset = DojoClass.objects.all()
    serializer_class = DojoClassSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # if instructor provided via instructor_id this will set it
        serializer.save()

class DojoClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DojoClass.objects.all()
    serializer_class = DojoClassSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Enrollment endpoints - user must be authenticated to enroll
class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # automatically set the student to the request user if they are a student
        serializer.save(student=self.request.user)

class EnrollmentDetailView(generics.RetrieveDestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

# Payment endpoints
class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # saving payment, leave validation to front/back (can be extended)
        serializer.save()

class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_stats(request):
    user = request.user
    if getattr(user, 'role', None) != 'admin':
        return Response({"detail": "Not authorized"}, status=403)
    data = {
        "totalStudents": User.objects.filter(role='student').count(),
        "totalClasses": DojoClass.objects.count(),
        "totalEnrollments": Enrollment.objects.count(),
        "activeInstructors": User.objects.filter(role='instructor').count()
    }
    return Response(data)