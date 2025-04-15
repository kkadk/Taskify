from rest_framework import serializers
from taskm.models import Task
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

VALID_DOMAINS = {
    'admin.task.com': 'Admin',
    'manager.task.com': 'Manager',
    'employee.task.com': 'Employee',
}

class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    assigned_to = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username'
    )
    class Meta:
        model = Task
        fields = '__all__'
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        request = self.context.get('request')
        assigned_to = data.get('assigned_to')
        if request.user == assigned_to:
            raise serializers.ValidationError("You cannot assign a task to yourself.")
        if request.user.groups.filter(name='Employee').exists():
            raise serializers.ValidationError("Employees cannot create or assign tasks.")
        if request.user.groups.filter(name='Manager').exists():
            if assigned_to.groups.filter(name='Admin').exists():
                raise serializers.ValidationError("Managers cannot assign tasks to admins.")
        return data
    
    def validate_state(self, value):
        if value not in ['Pending', 'Completed']:
            raise serializers.ValidationError("State must be either 'Pending' or 'Completed'.")
        return value


    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.groups.filter(name='Employee').exists():
            allowed_fields = ['state']
            for field in validated_data:
                if field not in allowed_fields:
                    raise serializers.ValidationError(f"Employees can only update the 'state' field.")
        return super().update(instance, validated_data)
    

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        domain = value.split('@')[-1]
        if domain not in VALID_DOMAINS:
            raise ValidationError(f"Email must be from one of the following domains: {', '.join(VALID_DOMAINS.keys())}.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        domain = email.split('@')[-1]
        role = VALID_DOMAINS[domain]

        user = User.objects.create_user(
            username=validated_data['username'],
            email=email,
            password=validated_data['password']
        )
        user.is_active = False  
        user.save()

        group = Group.objects.get(name=role)
        user.groups.add(group)
        
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user