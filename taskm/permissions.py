from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()
    
class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Employee').exists()
      
class TaskPermissions(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.groups.filter(name='Admin').exists():
            return True

        elif user.groups.filter(name='Manager').exists():
            if request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
                return obj.created_by == user
            return True

        elif user.groups.filter(name='Employee').exists():
            if request.method == 'GET':
                return True
            elif request.method == 'PATCH':
                return obj.assigned_to == user and 'state' in request.data.keys()
        
        return False