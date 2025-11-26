from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='home'),
    path('sobre/', SobreView.as_view(), name='sobre'),
    path('servicos/', ServicosView.as_view(), name='servicos'),
    path('profissionais/', ProfissionaisView.as_view(), name='profissionais'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('contato/', ContatoView.as_view(), name='contato'),
    path('agendamento/', AgendamentoView.as_view(), name='agendamento'),
    path('apoio_emocional/', ApoioEmocionalView.as_view(), name='apoio_emocional'),
    path('emergencias/', EmergenciaView.as_view(), name='emergencias'),

    
    # URLs de Gerenciamento de Horários
    path('horarios/', HorarioDisponivelListView.as_view(), name='horarios_list'),
    path('horarios/novo/', HorarioDisponivelCreateView.as_view(), name='horarios_create'),
    
    # URLs de Autenticação
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', perfil_view, name='perfil'),
    
    # API para chat com IA
    path('api/chat-ia/', chat_ia_api, name='chat_ia_api'),
]
