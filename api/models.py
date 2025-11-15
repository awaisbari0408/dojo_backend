from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"


class DojoClass(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    schedule = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(default=20)

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    martial_class = models.ForeignKey(DojoClass, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.martial_class.name}"


class Payment(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('pending', 'Pending')])

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.status} - {self.amount}"


