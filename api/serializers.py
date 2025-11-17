from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import DojoClass, Enrollment, Payment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims 
        token['username'] = user.username
        # If the User model uses 'role' as the field name, include it 
        token['role'] = getattr(user, 'role', 'student')
        token['user_id'] = user.id
        return token

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name", "role")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class DojoClassSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    instructor_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.filter(role='instructor'), source='instructor')

    class Meta:
        model = DojoClass
        fields = ("id", "name", "description", "instructor", "instructor_id", "schedule", "capacity")

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.filter(role='student'), source='student')
    martial_class = DojoClassSerializer(read_only=True)
    martial_class_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=DojoClass.objects.all(), source='martial_class')

    class Meta:
        model = Enrollment
        fields = ("id", "student", "student_id", "martial_class", "martial_class_id", "date_enrolled")

class PaymentSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True)
    enrollment_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Enrollment.objects.all(), source='enrollment')

    class Meta:
        model = Payment
        fields = ("id", "enrollment", "enrollment_id", "amount", "date", "status", "description")
