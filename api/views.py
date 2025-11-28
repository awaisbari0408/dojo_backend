from rest_framework import generics, permissions, exceptions
from django.contrib.auth import get_user_model
from django.db import models
from .models import DojoClass, Enrollment, Payment, Schedule
from .serializers import UserSerializer, DojoClassSerializer, EnrollmentSerializer, PaymentSerializer, ScheduleSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAdminUser

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
        # only allow admin or instructor to create classes
        user = self.request.user
        if getattr(user, 'role', None) not in ['admin', 'instructor']:
            raise exceptions.PermissionDenied("Only admins or instructors can create classes.")
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

# Schedule Endpoints
class ScheduleListCreateView(generics.ListCreateAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def get_permissions(self):
        # allow anyone to list; only authenticated instructors/admins can create (adjust as needed)
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # optional: restrict creation to instructors/admins
        serializer.save()

class ScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

class IsAdmin(permissions.BasePermission):
    """Allow only admins to access."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class UserListView(generics.ListAPIView):
    """
    List users. Optional filter: ?role=instructor (or admin/student)
    Requires authentication.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        return qs


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve / update / delete a user (admin only for destructive actions in real app).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
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

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_schedule(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    schedules = Schedule.objects.filter(dojo_class__in=[e.martial_class for e in enrollments])
    serializer = ScheduleSerializer(schedules, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def list_instructors(request):
    instructors = User.objects.filter(role='instructor')
    data = UserSerializer(instructors, many=True).data
    return Response(data)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def enrollment_reports(request):
    total_enrollments = Enrollment.objects.count()

    # Count enrollments grouped by class name
    class_stats = (
        Enrollment.objects
        .values("martial_class__name")
        .annotate(count=models.Count("id"))
        .order_by("-count")
    )

    return Response({
        "total_enrollments": total_enrollments,
        "class_summary": class_stats
    })