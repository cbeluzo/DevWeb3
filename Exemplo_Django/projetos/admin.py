from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Projeto, Tarefa


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ("nome", "responsavel", "data_inicio", "data_fim")
    search_fields = ("nome", "responsavel__username")


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "projeto", "concluida")
    list_filter = ("concluida",)
