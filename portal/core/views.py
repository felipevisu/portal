from django.http import HttpResponse
from django.template import loader
from django.views.generic import TemplateView

from portal.customer.models import Client


class TenantView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tenants_list"] = Client.objects.all()
        return context
