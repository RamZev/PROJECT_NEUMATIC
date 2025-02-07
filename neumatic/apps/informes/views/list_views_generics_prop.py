# neumatic\apps\informes\views\list_views_generics_prop.py
from django.views.generic import FormView, TemplateView

#-- Recursos necesarios para proteger las rutas.
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


# -- Vistas Genéricas Basada en Clases -----------------------------------------------
@method_decorator(login_required, name='dispatch')
class InformeFormView(FormView):
	pass

@method_decorator(login_required, name='dispatch')
class InformeTemplateView(TemplateView):
	pass

