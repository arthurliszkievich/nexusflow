from django.db.models import F, Q, QuerySet

from colaboradores.models import Colaborador
from processos.models import Processo

def listar_processos_otimizado() -> QuerySet[Processo]:
    """
    Retorna todos os processos evitando o problema N+1:
    - select_related: resolve ForeignKeys (1-para-1 / N-para-1) via SQL JOIN
    - prefetch_related: resolve relações reversas (1-para-N) via WHERE IN (...).
    """

    return Processo.objects.select_related(
        "solicitante",
        "aprovador",
        "departamento_destino",
    ).prefetch_related(
        "historicos",
        "historicos__autor",
    )

def buscar_processos_envolvendo_usuario(usuario: Colaborador) -> QuerySet[Processo]:
    """
    Retorna processos onde o usuário é solicitante OU aprovador, 
    mas impede que o aprovador veja processos que ainda estão em
    RASCUNHO.
    """

    filtro_envolvimento = Q(solicitante=usuario) | Q(aprovador=usuario)
    filtro_visibilidade = Q(solicitante=usuario) | ~Q(status=Processo.Status.RASCUNHO)

    return listar_processos_otimizado().filter(
        filtro_envolvimento & filtro_visibilidade
    )

def buscar_processo_conflito_aprovacao() -> QuerySet[Processo]:
    """
    Exemplo de auditoria usando F(): encontra qualquer processo onde
    a coluna solicitante_id seja igual à coluna aprovador_id.
    """

    return listar_processos_otimizado().filter(
        aprovador__isnull=False,
        solicitante_id=F("aprovador_id")
    )