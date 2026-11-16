import pytest
from django.db import IntegrityError
from django.db.models import F
from model_bakery import baker

from colaboradores.models import Colaborador, Departamento
from processos.models import HistoricoProcesso, Processo
from processos.selectors import (
    buscar_processos_envolvendo_usuario,
    listar_processos_otimizado,
)


@pytest.mark.django_db
def test_listar_processos_otimizado_evita_n_mais_1(django_assert_num_queries):
    depto = baker.make(Departamento, nome="Tecnologia", sigla="TI")
    solicitante = baker.make(Colaborador, matricula="MAT001", departamento=depto)
    autor = baker.make(Colaborador, matricula="MAT002", departamento=depto)

    # Cria 5 processos e 2 históricos para cada um (10 históricos no total)
    for i in range(5):
        proc = baker.make(
            Processo,
            titulo=f"Processo {i}",
            tipo=Processo.Tipo.CHAMADO,
            solicitante=solicitante,
            departamento_destino=depto,
        )
        baker.make(
            HistoricoProcesso,
            processo=proc,
            autor=autor,
            status_anterior=Processo.Status.RASCUNHO,
            status_novo=Processo.Status.SUBMETIDO,
            _quantity=2,
        )

    # Sem otimização, isso faria mais de 25 queries!
    # Com select_related + prefetch_related:
    # 1 query (Processo + JOINs) + 1 query (historicos) + 1 query (historicos__autor) = 3 queries!
    with django_assert_num_queries(3):
        processos = list(listar_processos_otimizado())
        for p in processos:
            _ = p.solicitante.matricula
            _ = p.departamento_destino.sigla
            for h in p.historicos.all():
                _ = h.autor.matricula

    assert len(processos) == 5


@pytest.mark.django_db
def test_filtro_q_esconde_rascunho_para_aprovador():
    solicitante = baker.make(Colaborador, matricula="MAT010")
    aprovador = baker.make(Colaborador, matricula="MAT020")

    rascunho = baker.make(
        Processo,
        tipo=Processo.Tipo.CHAMADO,
        status=Processo.Status.RASCUNHO,
        solicitante=solicitante,
        aprovador=aprovador,
    )
    submetido = baker.make(
        Processo,
        tipo=Processo.Tipo.CHAMADO,
        status=Processo.Status.SUBMETIDO,
        solicitante=solicitante,
        aprovador=aprovador,
    )

    visiveis_aprovador = list(buscar_processos_envolvendo_usuario(aprovador))
    visiveis_solicitante = list(buscar_processos_envolvendo_usuario(solicitante))

    assert visiveis_aprovador == [submetido]
    assert set(visiveis_solicitante) == {rascunho, submetido}


@pytest.mark.django_db
def test_atualizacao_atomica_saldo_ferias_com_f():
    colab = baker.make(Colaborador, matricula="MAT030", saldo_ferias_dias=30)

    Colaborador.objects.filter(pk=colab.pk).update(
        saldo_ferias_dias=F("saldo_ferias_dias") - 5
    )
    colab.refresh_from_db()

    assert colab.saldo_ferias_dias == 25


@pytest.mark.django_db
def test_constraint_banco_impede_ferias_sem_dias():
    solicitante = baker.make(Colaborador, matricula="MAT040")

    with pytest.raises(IntegrityError):
        Processo.objects.create(
            titulo="Férias inválidas",
            descricao="Tentando salvar férias sem informar dias",
            tipo=Processo.Tipo.FERIAS,
            dias_solicitados=None,
            solicitante=solicitante,
        )