from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps

def user_type_required(*allowed_user_types):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user_profile = getattr(request.user, 'profile', None)
            actual_user_type = user_profile.user_type if user_profile else None

            if actual_user_type in allowed_user_types:
                return view_func(request, *args, **kwargs)
            else:
                # Redirect to the appropriate dashboard based on actual user_type
                if actual_user_type == 'manager':
                    return redirect('project_management:home_manager')
                elif actual_user_type == 'warehouse':
                    return redirect('warehouse:home_warehouse')
                elif actual_user_type == 'procurement':
                    return redirect('procurement:home_procurement')
                elif actual_user_type == 'supplier':
                    return redirect('supply:home_supplier')
                else:
                    return redirect('user_management:login')
        return wrapper
    return decorator

