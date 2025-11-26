from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Psicologo, Consulta, InteracaoIA, HorarioDisponivel
from .forms import RegistroForm, LoginForm

import random

# --- Views de Páginas Estáticas ---

class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


class SobreView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'sobre.html')


class ServicosView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'servicos.html')


class ProfissionaisView(View):
    def get(self, request, *args, **kwargs):
        psicologos = Psicologo.objects.all()
        context = {'psicologos': psicologos}
        return render(request, 'profissionais.html', context)


class BlogView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'blog.html')


class ContatoView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'contato.html')
    
    def post(self, request, *args, **kwargs):
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')
        aceito_termos = request.POST.get('aceito_termos')
        aceito_newsletter = request.POST.get('aceito_newsletter')
        
        if not all([nome, email, assunto, mensagem, aceito_termos]):
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return render(request, 'contato.html')
        
        # Simulação de envio de e-mail ou salvamento de contato
        try:
            # Aqui você implementaria a lógica real de envio de e-mail ou salvamento no DB
            messages.success(request, 'Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.')
            return redirect('contato')
        except Exception as e:
            messages.error(request, 'Ocorreu um erro ao enviar sua mensagem. Tente novamente.')
            return render(request, 'contato.html')


# --- Views de Gerenciamento de Horários ---

@method_decorator(login_required, name='dispatch')
class HorarioDisponivelListView(View):
    def get(self, request, *args, **kwargs):
        # ⚠️ Apenas psicólogos devem acessar esta view.
        # Implementação de verificação de perfil de psicólogo é necessária.
        try:
            psicologo = Psicologo.objects.get(usuario=request.user)
        except Psicologo.DoesNotExist:
            messages.error(request, 'Acesso negado. Você não está cadastrado como psicólogo.')
            return redirect('home')
        
        horarios = HorarioDisponivel.objects.filter(psicologo=psicologo).order_by('dia_semana', 'hora_inicio')
        
        context = {
            'psicologo': psicologo,
            'horarios': horarios,
            'dias_semana': HorarioDisponivel.DIA_CHOICES # Para exibir o nome do dia
        }
        return render(request, 'horarios_list.html', context) # Template a ser criado

@method_decorator(login_required, name='dispatch')
class HorarioDisponivelCreateView(View):
    def get(self, request, *args, **kwargs):
        try:
            psicologo = Psicologo.objects.get(usuario=request.user)
        except Psicologo.DoesNotExist:
            messages.error(request, 'Acesso negado. Você não está cadastrado como psicólogo.')
            return redirect('home')
        
        context = {
            'psicologo': psicologo,
            'dias_semana': HorarioDisponivel.DIA_CHOICES
        }
        return render(request, 'horarios_create.html', context) # Template a ser criado

    def post(self, request, *args, **kwargs):
        try:
            psicologo = Psicologo.objects.get(usuario=request.user)
        except Psicologo.DoesNotExist:
            messages.error(request, 'Acesso negado. Você não está cadastrado como psicólogo.')
            return redirect('home')
        
        dia_semana = request.POST.get('dia_semana')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim = request.POST.get('hora_fim')
        
        if not all([dia_semana, hora_inicio, hora_fim]):
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect('horarios_create')
        
        try:
            HorarioDisponivel.objects.create(
                psicologo=psicologo,
                dia_semana=dia_semana,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim
            )
            messages.success(request, 'Horário de disponibilidade criado com sucesso!')
            return redirect('horarios_list')
        except Exception as e:
            messages.error(request, f'Erro ao criar horário: {e}')
            return redirect('horarios_create')


# --- Views de Agendamento ---

@method_decorator(login_required, name='dispatch')
class AgendamentoView(View):
    def get(self, request, *args, **kwargs):
        psicologos = Psicologo.objects.all()
        context = {'psicologos': psicologos}
        return render(request, 'agendamento.html', context)
    
    def post(self, request, *args, **kwargs):
        # A verificação de login é feita pelo decorador @login_required
        
        psicologo_id = request.POST.get('psicologo')
        data = request.POST.get('data')
        horario = request.POST.get('horario')
        
        if not all([psicologo_id, data, horario]):
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect('agendamento')
        
        try:
            psicologo = get_object_or_404(Psicologo, id=psicologo_id)
            
            # ⚠️ Correção: use os nomes de campo ATUALIZADOS (sem 'id_')
            consulta_existente = Consulta.objects.filter(
                psicologo=psicologo,
                data=data,
                horario=horario,
                status='agendada'
            ).exists()
            
            if consulta_existente:
                messages.error(request, 'Este horário já está ocupado. Escolha outro horário.')
                return redirect('agendamento')
            
            # ⚠️ Correção: use os nomes corretos ao criar
            consulta = Consulta.objects.create(
                usuario=request.user,
                psicologo=psicologo,
                data=data,
                horario=horario,
                status='agendada'
            )
            
            messages.success(request, f'Consulta agendada com sucesso para {data} às {horario} com {psicologo.nome}!')
            return redirect('agendamento')
            
        except Exception as e:
            messages.error(request, 'Ocorreu um erro ao agendar a consulta. Tente novamente.')
            return redirect('agendamento')


# --- Views de Apoio Emocional (IA) ---

class ApoioEmocionalView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'apoio_emocional.html')
    
    def post(self, request, *args, **kwargs):
        mensagem_usuario = request.POST.get('mensagem')
        
        if not mensagem_usuario:
            return JsonResponse({'error': 'Mensagem não pode estar vazia'}, status=400)
        
        try:
            resposta_ia = self.gerar_resposta_ia(mensagem_usuario)
            
            if request.user.is_authenticated:
                # ⚠️ Correção: use 'usuario', não 'id_usuario'
                InteracaoIA.objects.create(
                    usuario=request.user,
                    mensagem_usuario=mensagem_usuario,
                    resposta_ia=resposta_ia
                )
            
            return JsonResponse({
                'resposta': resposta_ia,
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            return JsonResponse({'error': 'Erro interno do servidor'}, status=500)
    
    def gerar_resposta_ia(self, mensagem):
        respostas_exemplo = [
            "Entendo que você está passando por um momento difícil. É importante reconhecer seus sentimentos. Que tal tentarmos um exercício de respiração?",
            "Obrigado por compartilhar isso comigo. Seus sentimentos são válidos. Como posso te ajudar melhor neste momento?",
            "Percebo que você está enfrentando desafios. Lembre-se de que buscar ajuda é um sinal de força, não de fraqueza.",
            "É normal sentir-se assim às vezes. Vamos trabalhar juntos para encontrar estratégias que possam te ajudar.",
        ]
        
        mensagem_lower = mensagem.lower()
        
        if any(palavra in mensagem_lower for palavra in ['ansioso', 'ansiedade', 'nervoso']):
            return "Entendo que você está sentindo ansiedade. Vamos tentar um exercício de respiração: inspire por 4 segundos, segure por 4, expire por 6. Repita algumas vezes. Como você está se sentindo agora?"
        
        elif any(palavra in mensagem_lower for palavra in ['triste', 'deprimido', 'sozinho']):
            return "Sinto muito que você esteja se sentindo assim. Seus sentimentos são válidos e você não está sozinho. Às vezes, conversar sobre o que está acontecendo pode ajudar. Gostaria de me contar mais sobre o que está te deixando triste?"
        
        elif any(palavra in mensagem_lower for palavra in ['estresse', 'estressado', 'pressão']):
            return "O estresse pode ser muito desafiador. Uma técnica que pode ajudar é a regra 5-4-3-2-1: identifique 5 coisas que você pode ver, 4 que pode tocar, 3 que pode ouvir, 2 que pode cheirar e 1 que pode saborear. Isso pode te ajudar a se conectar com o momento presente."
        
        else:
            return random.choice(respostas_exemplo)


class EmergenciaView(View):
     def get(self, request, *args, **kwargs):
        return render(request, 'emergencias.html')


# --- Views de Autenticação ---

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True # Ativa o usuário por padrão
            user.save()
            messages.success(request, f'Conta criada com sucesso para {user.username}! Você já pode fazer login.')
            return redirect('login')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = RegistroForm()
                
    return render(request, 'registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo(a) de volta, {user.first_name}!')
                return redirect('home')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta com sucesso.')
    return redirect('login')


@login_required
def perfil_view(request):
    if request.method == 'POST':
        # Lógica para salvar alterações no perfil
        # (Não implementada no código original, mas o template está pronto)
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('perfil')
    
    context = {
        'usuario': request.user,
        # Adicione aqui dados de consultas e interações com IA se necessário
    }
    return render(request, 'perfil.html', context)

# --- API para chat com IA ---

def chat_ia_api(request):
    """
    Simula a resposta de uma IA para o chat de apoio emocional.
    """
    if request.method == 'POST':
        mensagem_usuario = request.POST.get('mensagem')
        
        if not mensagem_usuario:
            return JsonResponse({'error': 'Mensagem não pode estar vazia'}, status=400)
        
        # Lógica de simulação de resposta da IA (copiada da ApoioEmocionalView)
        respostas_exemplo = [
            "Entendo que você está passando por um momento difícil. É importante reconhecer seus sentimentos. Que tal tentarmos um exercício de respiração?",
            "Obrigado por compartilhar isso comigo. Seus sentimentos são válidos. Como posso te ajudar melhor neste momento?",
            "Percebo que você está enfrentando desafios. Lembre-se de que buscar ajuda é um sinal de força, não de fraqueza.",
            "É normal sentir-se assim às vezes. Vamos trabalhar juntos para encontrar estratégias que possam te ajudar.",
        ]
        
        mensagem_lower = mensagem_usuario.lower()
        
        if any(palavra in mensagem_lower for palavra in ['ansioso', 'ansiedade', 'nervoso']):
            resposta_ia = "Entendo que você está sentindo ansiedade. Vamos tentar um exercício de respiração: inspire por 4 segundos, segure por 4, expire por 6. Repita algumas vezes. Como você está se sentindo agora?"
        
        elif any(palavra in mensagem_lower for palavra in ['triste', 'deprimido', 'sozinho']):
            resposta_ia = "Sinto muito que você esteja se sentindo assim. Seus sentimentos são válidos e você não está sozinho. Às vezes, conversar sobre o que está acontecendo pode ajudar. Gostaria de me contar mais sobre o que está te deixando triste?"
        
        elif any(palavra in mensagem_lower for palavra in ['estresse', 'estressado', 'pressão']):
            resposta_ia = "O estresse pode ser muito desafiador. Uma técnica que pode ajudar é a regra 5-4-3-2-1: identifique 5 coisas que você pode ver, 4 que pode tocar, 3 que pode ouvir, 2 que pode cheirar e 1 que pode saborear. Isso pode te ajudar a se conectar com o momento presente."
        
        else:
            resposta_ia = random.choice(respostas_exemplo)
        
        try:
            if request.user.is_authenticated:
                InteracaoIA.objects.create(
                    usuario=request.user,
                    mensagem_usuario=mensagem_usuario,
                    resposta_ia=resposta_ia
                )
            
            return JsonResponse({
                'resposta': resposta_ia,
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            return JsonResponse({'error': 'Erro interno do servidor'}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)
