from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps

def user_type_required(required_user_type):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user_profile = getattr(request.user, 'profile', None)
            if user_profile and user_profile.user_type == required_user_type:
                return view_func(request, *args, **kwargs)
            else:
                # Redirect to the appropriate dashboard based on actual user_type
                actual_user_type = user_profile.user_type if user_profile else None

                if actual_user_type == 'manager':
                    return redirect('project_management:home_manager')
                elif actual_user_type == 'warehouse':
                    return redirect('warehouse:home_warehouse')
                elif actual_user_type == 'procurement':
                    return redirect('procurement:home_procurement')
                elif actual_user_type == 'supplier':
                    return redirect('supply:home_supplier')
                else:
                    # Fallback redirect (e.g., login page)
                    return redirect('user_management:login')

        return wrapper
    return decorator
