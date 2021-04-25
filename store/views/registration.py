from store.forms import RegistrationForm
from django_registration.backends.one_step.views import RegistrationView as BaseRegistrationView


class RegistrationView(BaseRegistrationView):
    form_class = RegistrationForm
