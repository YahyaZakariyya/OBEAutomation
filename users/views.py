from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # Update with your login template path

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        # Redirect based on user role
        if self.request.user.is_superuser:
            return redirect(reverse('admin-dashboard'))  # Update with your admin dashboard URL name
        else:
            return redirect(reverse('user-dashboard'))  # Update with your user dashboard URL name
