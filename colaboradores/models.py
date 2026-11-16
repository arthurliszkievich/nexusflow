from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class Departamento(models.Model):
    nome = models.CharField(max_length=100, unique =True)
    sigla = models.CharField(max_length=10, unique=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ["nome"]

    def __str__(self) -> str:
        return f"{self.sigla} - {self.nome}"

class Colaborador(AbstractUser):
    class Papel(models.TextChoices):
        COLABORADOR = "COLABORADOR", "Colaborador"
        GESTOR = "GESTOR", "Gestor"
        RH = "RH", "Recursos Humanos"
    
    matricula = models.CharField(max_length=20, unique=True)
    papel = models.CharField(
        max_length=20,
        choices=Papel.choices,
        default=Papel.COLABORADOR,
        db_index=True,
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name="colaboradores",
        null=True,
        blank=True,
    )
    gestor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinados",
    )
    saldo_ferias_dias = models.PositiveSmallIntegerField(default=30)

    class Meta:
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        indexes = [
            models.Index(
                fields=["departamento", "papel"],
                name="idx_colab_depto_papel",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(gestor__isnull=True) |
                ~Q(id=F("gestor_id")),
                name="chk_colaborador_nao_proprio_gestor",
            ),
            models.CheckConstraint(
                condition=Q(saldo_ferias_dias__lte=60),
                name="chk_saldo_ferias_maximo",
            ),
        ]
    def __str__(self) -> str:
        return f"{self.matricula} - {self.get_full_name() or self.username}"