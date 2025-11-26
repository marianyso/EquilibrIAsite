from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# ========== MODELO DE USUÁRIO PERSONALIZADO ==========
class Usuario(AbstractUser):
    """
    Modelo de usuário estendido.
    Herda: username, email, first_name, last_name, password, is_staff, etc.
    """
    # Opcional: tornar e-mail obrigatório (recomendado)
    email = models.EmailField(_('endereço de e-mail'), unique=True)

    # Campos adicionais podem ser adicionados aqui

    def __str__(self):
        # Corrigido para usar self.get_full_name() que é um método do AbstractUser
        return self.get_full_name() or self.username

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"


# ========== MODELO DE PSICÓLOGO ==========
class Psicologo(models.Model):
    """
    Representa um psicólogo registrado no sistema.
    Deve estar vinculado a um usuário para autenticação.
    """
    # Corrigido para usar 'Usuario' diretamente, pois está no mesmo app
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name="Usuário vinculado"
    )
    nome = models.CharField(max_length=150, verbose_name="Nome completo")
    crp = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="CRP",
        help_text="Ex: 01/123456",
        validators=[
            RegexValidator(
                regex=r'^\d{2}/\d{6}$',
                message="O CRP deve seguir o formato XX/XXXXXX (ex: 06/123456)."
            )
        ]
    )
    especialidades = models.TextField(
        blank=True,
        verbose_name="Especialidades",
        help_text="Ex: Terapia cognitivo-comportamental, Ansiedade, Depressão"
    )

    def __str__(self):
        return f"{self.nome} (CRP: {self.crp})"

    class Meta:
        verbose_name = "Psicólogo"
        verbose_name_plural = "Psicólogos"


# ========== MODELO DE CONSULTA ==========
class Consulta(models.Model):
    """
    Representa um agendamento entre um usuário e um psicólogo.
    """
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('confirmada', 'Confirmada'),
        ('realizada', 'Realizada'),
        ('cancelada_paciente', 'Cancelada pelo paciente'),
        ('cancelada_psicologo', 'Cancelada pelo psicólogo'),
        ('faltou', 'Paciente não compareceu'),
    ]

    # Corrigido para usar 'Usuario' diretamente
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='consultas_como_paciente',
        verbose_name="Paciente"
    )
    psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.CASCADE,
        related_name='consultas',
        verbose_name="Psicólogo"
    )
    data = models.DateField(verbose_name="Data da consulta")
    horario = models.TimeField(verbose_name="Horário da consulta")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='agendada',
        verbose_name="Status"
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consulta: {self.usuario} → {self.psicologo} em {self.data} às {self.horario}"

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        unique_together = ('psicologo', 'data', 'horario')  # Evita duplicatas no mesmo horário


# ========== MODELO DE HORÁRIO DISPONÍVEL ==========
class HorarioDisponivel(models.Model):
    """
    Define um bloco de horário disponível para um psicólogo em um dia específico.
    """
    DIA_CHOICES = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.CASCADE,
        related_name='horarios_list',
        verbose_name="Psicólogo"
    )
    dia_semana = models.IntegerField(
        choices=DIA_CHOICES,
        verbose_name="Dia da Semana"
    )
    hora_inicio = models.TimeField(verbose_name="Hora de Início")
    hora_fim = models.TimeField(verbose_name="Hora de Fim")

    def __str__(self):
        return f"{self.get_dia_semana_display()} de {self.hora_inicio.strftime('%H:%M')} a {self.hora_fim.strftime('%H:%M')} ({self.psicologo.nome})"

    class Meta:
        verbose_name = "Horário Disponível"
        verbose_name_plural = "Horários Disponíveis"
        unique_together = ('psicologo', 'dia_semana', 'hora_inicio', 'hora_fim') # Evita blocos duplicados

# ========== MODELO DE AGENDA (Simplificado) ==========
class Agenda(models.Model):
    """
    Modelo de Agenda simplificado. A disponibilidade detalhada
    é gerenciada pelo modelo HorarioDisponivel.
    """
    psicologo = models.OneToOneField(
        Psicologo,
        on_delete=models.CASCADE,
        verbose_name="Psicólogo"
    )
    # Campos de texto removidos, pois HorarioDisponivel gerencia isso.
    # Este modelo pode ser usado para configurações gerais da agenda.

    def __str__(self):
        return f"Agenda de {self.psicologo}"

    class Meta:
        verbose_name = "Agenda"
        verbose_name_plural = "Agendas"


# ========== MODELO DE AUTOAVALIAÇÃO EMOCIONAL ==========
class AutoavaliacaoEmocional(models.Model):
    """
    Armazena respostas do usuário a uma autoavaliação emocional (ex: escala de humor, ansiedade).
    """
    # Corrigido para usar 'Usuario' diretamente
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name="Paciente"
    )
    data = models.DateTimeField(auto_now_add=True)
    humor = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="De 1 (muito triste) a 10 (muito feliz)",
        verbose_name="Nível de humor"
    )
    ansiedade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="De 1 (nenhuma) a 10 (muita ansiedade)",
        verbose_name="Nível de ansiedade"
    )
    estresse = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="De 1 (nenhum) a 10 (muito estresse)",
        verbose_name="Nível de estresse"
    )
    observacoes = models.TextField(blank=True, verbose_name="Observações livres")

    def __str__(self):
        return f"Autoavaliação de {self.usuario} em {self.data.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Autoavaliação Emocional"
        verbose_name_plural = "Autoavaliações Emocionais"


# ========== MODELO DE INTERAÇÃO COM IA ==========
class InteracaoIA(models.Model):
    """
    Registra conversas entre o usuário e a IA (ex: chatbot de suporte emocional).
    """
    # Corrigido para usar 'Usuario' diretamente
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name="Paciente"
    )
    mensagem_usuario = models.TextField(verbose_name="Mensagem do usuário")
    resposta_ia = models.TextField(verbose_name="Resposta da IA")
    timestamp = models.DateTimeField(auto_now_add=True)
    autoavaliacao_relacionada = models.ForeignKey(
        AutoavaliacaoEmocional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Autoavaliação associada"
    )

    def __str__(self):
        return f"IA ↔ {self.usuario} em {self.timestamp.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Interação com IA"
        verbose_name_plural = "Interações com IA"


# ========== MODELO DE NOTIFICAÇÃO ==========
class Notificacao(models.Model):
    """
    Notificações enviadas ao usuário (ex: lembrete de consulta).
    """
    TIPO_CHOICES = [
        ('consulta', 'Consulta'),
        ('sistema', 'Sistema'),
        ('ia', 'Interação com IA'),
    ]

    # Corrigido para usar 'Usuario' diretamente
    destinatario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name="Destinatário"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='sistema')
    mensagem = models.TextField(verbose_name="Conteúdo")
    data_envio = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False, verbose_name="Lida")

    def __str__(self):
        return f"Notificação para {self.destinatario} em {self.data_envio.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-data_envio']


# ========== MODELO DE AVALIAÇÃO PÓS-CONSULTA ==========
class Avaliacao(models.Model):
    """
    Avaliação feita pelo paciente após uma consulta.
    """
    consulta = models.OneToOneField(
        Consulta,
        on_delete=models.CASCADE,
        verbose_name="Consulta avaliada"
    )
    nota = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Nota (1 a 5)"
    )
    comentario = models.TextField(blank=True, null=True, verbose_name="Comentário")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação da consulta {self.consulta.id} – Nota: {self.nota}"

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
