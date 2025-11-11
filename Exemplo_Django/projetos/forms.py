from django import forms
from .models import Projeto, Tarefa

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ["nome", "descricao", "data_inicio", "data_fim", "responsavel"]

class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ["projeto", "titulo", "descricao", "concluida"]
