from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(Usuario, UserAdmin) 
admin.site.register(Psicologo)
admin.site.register(Consulta)
admin.site.register(HorarioDisponivel)
admin.site.register(AutoavaliacaoEmocional)
admin.site.register(InteracaoIA)
admin.site.register(Notificacao)
admin.site.register(Avaliacao)
admin.site.register(Agenda)