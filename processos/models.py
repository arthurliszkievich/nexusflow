from django.conf import settings
from django.db import models
from django.db.models import Q

class Processo(models.Model):
    class Tipo(models.TextChoices):
        FERIAS = "FERIAS", "Solicitação de Férias"
        RECURSO = "RECURSO", "Solicitação de Recurso"
        CHAMADO = "CHAMADO", "Chamado de Departamento"

    class Status(models.TextChoices):
        RASCUNHO = "RASCUNHO", "Rascunho"
        SUBMETIDO = "SUBMETIDO", "Submetido"
        EM_APROVACAO = "EM_APROVACAO", "Em Aprovação"
        APROVADO = "APROVADO", "Aprovado"
        REPROVADO = "REPROVADO", "Reprovado"

    class Urgencia(models.TextChoices):
        BAIXA = "BAIXA", "Baixa"
        MEDIA = "MEDIA", "Média"
        ALTA = "ALTA", "Alta"
        CRITICA = "CRITICA", "Crítica"

    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RASCUNHO,
        db_index=True
    )
    urgencia = models.CharField(
        max_length=20,
        choices=Urgencia.choices,
        default=Urgencia.MEDIA,
    )
    dias_solicitados = models.PositiveSmallIntegerField(null=True, blank=True
    )

    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="processos_criados",
    )

    aprovador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="processos_para_aprovar"
    )

    departamento_destino = models.ForeignKey(
        "colaboradores.Departamento",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="processos_recebidos",
    )

    resumo_ia = models.TextField(blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Processo"
        verbose_name_plural = "Processos"
        ordering = ['-criado_em']
        indexes = [
            models.Index(
                fields=["status", "departamento_destino"],
                name="idx_proc_status_depto"
            ),
            models.Index(
                fields=["solicitante", "-criado_em"],
                name="idx_proc_solicitante_data"
            )
        ]
        constraints = [
                models.CheckConstraint(
                    condition=Q(tipo="FERIAS", dias_solicitados__isnull=False, dias_solicitados__gte=1) | ~Q(tipo="FERIAS"),
                    name="chk_ferias_exige_dias_solicitados",
                ),
            ]
    def __str__(self) -> str:
        return f"#{self.pk} [{self.status}] {self.titulo}"

class HistoricoProcesso(models.Model):
    processo = models.ForeignKey(
        Processo,
        on_delete=models.CASCADE,
        related_name="historicos",
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="acoes_processos",
    )
    status_anterior = models.CharField(max_length=20, choices=Processo.Status.choices)
    status_novo = models.CharField(max_length=20, choices=Processo.Status.choices)
    observacao = models.TextField(blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Histórico do Processo"
        verbose_name_plural = "Históricos dos Processos"
        ordering = ["criado_em"]
    def __str__(self) -> str:
        return f"Processo #{self.processo_id}: {self.status_anterior} -> {self.status_novo}"