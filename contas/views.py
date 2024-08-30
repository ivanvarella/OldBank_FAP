from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

# Para conseguir acessar a tabela Contas do banco de dados
# Usando o ORM do Django com a classe em models do App contas
from .models import Conta

# Importar a classe Movimentacao do models do App Movimentacoes
from movimentacoes.models import Movimentacao

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, date, timedelta

# Para conseguir tratar e enviar via contexto os dados das contas + user
# para o template de conta_cliente como Json e assim ser utilizado para
# alteração do DOM dinamicamente com Js
from django.utils.safestring import mark_safe
import json

# Para formatar_valor()
from decimal import Decimal

# Para calular saldo médio da conta
from django.db.models import Avg, Count, Prefetch, Q


# Create your views here.


# Função formatar os valores monetários antes de salvar no DB
def formatar_valor(valor):
    """
    Converte uma string de valor monetário para um float.
    Exemplo de entrada: 'R$ 1.000.000,00'
    Exemplo de saída: 1000000.00
    """
    # Remove o símbolo 'R$' e espaços
    valor = valor.replace("R$", "").replace(" ", "")

    # Remove os pontos que são separadores de milhar
    valor = valor.replace(".", "")

    # Substitui a vírgula por ponto para a conversão
    valor = valor.replace(",", ".")

    # Converte a string para float
    try:
        # valor_float = float(valor)
        valor_decimal = Decimal(valor)
    except ValueError:
        raise ValueError("O valor fornecido não é um formato numérico válido")

    return valor_decimal


# TODO Implementar os cáculos via triggers no banco
def calcular_saldo_medio(movimentacoes):

    # Calcula a média dos saldos_antes e saldo_apos
    saldo_medio = movimentacoes.aggregate(
        media_saldo_antes=Avg("saldo_antes"), media_saldo_apos=Avg("saldo_apos")
    )

    # Calcula a média geral dos saldos
    saldo_medio_total = (
        saldo_medio["media_saldo_antes"] + saldo_medio["media_saldo_apos"]
    ) / 2

    return saldo_medio_total


@login_required(login_url="/usuarios/logar")
def cadastrar_conta(request):

    if not request.user.is_superuser:
        messages.warning(
            request,
            "Acesso negado, somente Gerentes podem abrir novas contas ou editar contas.",
        )
        return redirect("conta_cliente")

    # Via link ou direto no navegador
    if request.method == "GET":

        # Pega do models os tipos de contas para preencher no select, caso alterado já altera no form automaticamente
        TIPO_CONTA_CHOICES = Conta.TIPO_CONTA_CHOICES

        # Filtra usuários que possuem menos de 2 contas ativas
        usuarios_banco = User.objects.annotate(
            num_contas_ativas=Count("conta", filter=Q(conta__ativa=True))
        ).filter(num_contas_ativas__lt=2)

        # Adiciona as contas ativas associadas aos usuários filtrados
        usuarios_com_contas = usuarios_banco.prefetch_related(
            Prefetch(
                "conta_set",
                queryset=Conta.objects.filter(ativa=True),
                to_attr="contas",  # Atributo personalizado onde as contas serão armazenadas
            )
        )

        return render(
            request,
            "cadastrar_conta.html",
            {
                "tipo_conta_choices": TIPO_CONTA_CHOICES,
                "usuarios_banco": usuarios_com_contas,
            },
        )

    # Se for via form (retorno do cadastro para processar)
    elif request.method == "POST":

        # Dados para a tabela Conta no DB
        cliente_id = request.POST.get("cliente")
        tipo_conta = request.POST.get("tipo_conta")
        saldo = formatar_valor(request.POST.get("saldo"))
        limite_especial = formatar_valor(request.POST.get("limite_especial"))
        # Verifica se o checkbox foi marcado:retorna True ou False para salvar no DB
        ativa = request.POST.get("ativa") == "on"

        try:
            tipo_conta = int(tipo_conta)
            saldo = float(saldo)
            limite_especial = float(limite_especial)
        except ValueError:
            messages.error(request, "Dados fornecidos são inválidos.")
            return redirect("cadastrar_conta")

        # Cria a nova conta no banco de dados
        try:
            # Obtém a instância do User usando o ID do cliente
            usuario = User.objects.get(id=cliente_id)

            # Verifica se o usuário já possui 2 contas ativas
            # Provavelmente não vai acontecer por já estou filtrando no
            # select das contas no method GET
            contas_ativas = Conta.objects.filter(id_user=usuario, ativa=True)
            if contas_ativas.count() >= 2:
                messages.error(request, "O usuário já possui 2 contas ativas.")
                return redirect("cadastrar_conta")

            # Verifica se o usuário já possui uma conta do mesmo tipo
            if contas_ativas.filter(tipo_conta=tipo_conta).exists():
                messages.error(request, "O usuário já possui uma conta desse tipo.")
                return redirect("cadastrar_conta")

            # Só é salvo caso as verioficações acima não retornarem...
            nova_conta = Conta.objects.create(
                id_user=usuario,
                tipo_conta=tipo_conta,
                saldo=saldo,
                limite_especial=limite_especial,
                ativa=ativa,
            )
            messages.success(request, "Conta criada com sucesso!")
            # Fazer o redirecionar para a página de listagem de contas ou outra página
            return redirect("cadastrar_conta")  # Temporario
        except Exception as e:
            messages.error(request, f"Erro ao criar conta: {e}")
            return redirect("cadastrar_conta")

    return render(request, "cadastro_conta.html")


@login_required(login_url="/usuarios/logar")
def editar_conta(request, numero_conta):
    """
    Edita os dados de uma conta existente.
    """

    # Obtém os dados da Conta e do Cliente
    dados_conta_cliente = get_object_or_404(Conta, numero_conta=numero_conta)
    dados_cliente = User.objects.get(id=dados_conta_cliente.id_user.id)

    if not request.user.is_superuser:
        messages.warning(
            request, "Acesso negado, somente Gerentes podem editar contas."
        )
        return redirect("conta_cliente")

    # Resgata os dados CHOICES da models
    TIPO_CONTA_CHOICES = Conta.TIPO_CONTA_CHOICES

    # Flag para edição de conta
    editar_conta = True

    # Via link ou direto no navegador
    if request.method == "GET":
        return render(
            request,
            "cadastrar_conta.html",
            {
                "tipo_conta_choices": TIPO_CONTA_CHOICES,
                "dados_conta_cliente": dados_conta_cliente,
                "dados_cliente": dados_cliente,
                "editar_conta": editar_conta,
            },
        )

    elif request.method == "POST":
        conta = get_object_or_404(Conta, numero_conta=numero_conta)

        # Resgatando os dados do formulário de edição de conta
        limite_especial = formatar_valor(request.POST.get("limite_especial"))
        ativa = request.POST.get("ativa") == "on"

        try:
            # Atualiza o limite especial
            conta.limite_especial = Decimal(limite_especial)

            # Verifica se a conta está sendo ativada
            if ativa and not conta.ativa:
                # Verifica se o usuário já possui 2 contas ativas
                contas_ativas = Conta.objects.filter(id_user=conta.id_user, ativa=True)
                if contas_ativas.count() >= 2:
                    messages.error(
                        request,
                        "O usuário já possui 2 contas ativas e não pode ativar outra.",
                    )
                    return render(
                        request,
                        "cadastrar_conta.html",
                        {
                            "tipo_conta_choices": TIPO_CONTA_CHOICES,
                            "dados_conta_cliente": dados_conta_cliente,
                            "dados_cliente": dados_cliente,
                            "editar_conta": editar_conta,
                        },
                    )

                # Verifica se o usuário já possui uma conta ativa do mesmo tipo
                if contas_ativas.filter(tipo_conta=conta.tipo_conta).exists():
                    messages.error(
                        request,
                        f"O usuário já possui uma conta do tipo {conta.get_tipo_conta_display()} ativa.",
                    )
                    return render(
                        request,
                        "cadastrar_conta.html",
                        {
                            "tipo_conta_choices": TIPO_CONTA_CHOICES,
                            "dados_conta_cliente": dados_conta_cliente,
                            "dados_cliente": dados_cliente,
                            "editar_conta": editar_conta,
                        },
                    )

            # Atualiza o status de ativação da conta
            conta.ativa = ativa

            conta.save()
            messages.success(request, "Conta atualizada com sucesso.")
        except ValueError:
            messages.error(
                request, "Erro ao atualizar a conta. Verifique os valores inseridos."
            )
            return render(
                request,
                "cadastrar_conta.html",
                {
                    "tipo_conta_choices": TIPO_CONTA_CHOICES,
                    "dados_conta_cliente": dados_conta_cliente,
                    "dados_cliente": dados_cliente,
                    "editar_conta": editar_conta,
                },
            )

        return redirect("listar_contas")


@login_required(login_url="/usuarios/logar")
def conta_cliente(request):

    # Se veio do selecionar_conta: Regasta a conta_selecionada
    conta_selecionada_id = request.session.get("conta_selecionada")

    if not conta_selecionada_id:
        # Verificação das contas do usuario
        # Verifica as contas ATIVAS do usuário autenticado
        contas_usuario = Conta.objects.filter(id_user=request.user.id, ativa=True)
        num_contas = contas_usuario.count()  # Conta o número de contas associadas

        # Quando o usuário só tiver 1 conta, não precisa fazer nenhuma verificação,
        # somente carregar os dados da página conta_cliente normalmente
        if num_contas == 0:
            # Se não for Gerente
            if not request.user.is_superuser:
                messages.add_message(
                    request,
                    constants.WARNING,
                    "Ainda não possui Contas Ativas no Banco.",
                )
                return redirect("editar_usuario")
            # Se for Gerente
            else:
                messages.add_message(
                    request,
                    constants.WARNING,
                    "Ainda não possui Contas Ativas no Banco.",
                )
                return redirect("listar_contas")
        elif num_contas > 1:
            if not request.user.is_superuser:
                return redirect("selecionar_conta")
            else:
                return redirect("listar_contas")

    # Via link ou direto no navegador
    if request.method == "GET":
        # Só pega esses dados da conta pelo usuário logado, se não tiver sido passado
        # a conta na sessão pelo selecionar_conta
        if not conta_selecionada_id:
            dados_conta_cliente = Conta.objects.get(id_user=request.user.id)
        else:
            dados_conta_cliente = Conta.objects.get(id=conta_selecionada_id)
        dados_cliente = User.objects.get(id=request.user.id)
        # Apesar as últimas 3 movimentações da conta
        dados_movimentacoes = Movimentacao.objects.filter(
            conta=dados_conta_cliente
        ).order_by("-data_movimentacao")[:3]
        tipo_movimentacao_choices = Movimentacao.TIPO_MOVIMENTACAO_CHOICES

        # Obter os dados para popular o select das contas para transferencia
        # select_related('id_user'): Isso faz um INNER JOIN implícito entre Conta e User,
        # garantindo que se obtenha apenas as contas que têm um usuário associado e
        # trazendo os dados desses usuários em uma única consulta ao banco de dados.
        # contas_users = Conta.objects.select_related("id_user").all()
        contas_users = (
            Conta.objects.select_related("id_user")
            .values(
                "numero_conta",
                "tipo_conta",
                "id_user__first_name",
                "id_user__last_name",
            )
            .filter(ativa=True)
        )

        tipo_conta_choices = Conta.TIPO_CONTA_CHOICES

        return render(
            request,
            "conta_cliente.html",
            {
                "dados_conta_cliente": dados_conta_cliente,
                "dados_cliente": dados_cliente,
                "dados_movimentacoes": dados_movimentacoes,
                "tipo_movimentacao_choices": tipo_movimentacao_choices,
                "contas_users": contas_users,
                "tipo_conta_choices": tipo_conta_choices,
            },
        )
    elif request.method == "POST":

        # Add a movimentacao (saque, deposito ou transferencia - Não funcionando ainda)
        operacao = request.POST.get("operacao")

        if operacao == "deposito":
            valor_deposito = formatar_valor(request.POST.get("valor_deposito"))

            # if valor_deposito <= 0:
            if valor_deposito <= Decimal("0.00"):
                messages.error(
                    request,
                    "Valor de depósito inválido.\nNão é possível realizar o depósito de R$ 0,00 reais.",
                )
            else:
                # Só pega esses dados da conta pelo usuário logado, se não tiver sido passado
                # a conta na sessão pelo selecionar_conta
                if not conta_selecionada_id:
                    dados_conta_cliente = Conta.objects.get(id_user=request.user.id)
                else:
                    dados_conta_cliente = Conta.objects.get(id=conta_selecionada_id)
                # dados_conta_cliente = Conta.objects.get(id_user=request.user.id)
                saldo = Decimal(dados_conta_cliente.saldo)
                # saldo = float(dados_conta_cliente.saldo)

                # Calcula novo saldo após operação de depósito
                saldo_atualizado = saldo + valor_deposito
                data_atual = datetime.now()

                # Salva a movimentação no banco
                try:
                    nova_movimentacao = Movimentacao.objects.create(
                        conta=dados_conta_cliente,
                        tipo_movimentacao=2,  # Depósito
                        valor=valor_deposito,
                        data_movimentacao=data_atual,
                    )

                    # Atualiza o saldo da conta no banco
                    dados_conta_cliente.saldo = saldo_atualizado
                    dados_conta_cliente.save()

                    messages.success(request, "Depósto realizado com sucesso!")

                except Exception as e:
                    # Não precisa redirecionar aqui pois está renderizando a página no final com a mensagem de erro
                    messages.error(request, f"Erro ao tentar realizar o depósito: {e}")

        elif operacao == "saque":
            valor_saque = formatar_valor(request.POST.get("valor_saque"))
            # if valor_saque <= 0:
            if valor_saque <= Decimal("0.00"):
                messages.error(
                    request,
                    "Valor de saque inválido.\nNão é possível realizar o saque de R$ 0,00 reais.",
                )
            else:
                sacou = False
                # Só pega esses dados da conta pelo usuário logado, se não tiver sido passado
                # a conta na sessão pelo selecionar_conta
                if not conta_selecionada_id:
                    dados_conta_cliente = Conta.objects.get(id_user=request.user.id)
                else:
                    dados_conta_cliente = Conta.objects.get(id=conta_selecionada_id)
                # dados_conta_cliente = Conta.objects.get(id_user=request.user.id)
                saldo = Decimal(dados_conta_cliente.saldo)
                limite_especial = Decimal(dados_conta_cliente.limite_especial)

                # Possui saldo suficiente
                if saldo >= valor_saque:
                    saldo_atualizado = saldo - valor_saque
                    data_atual = datetime.now()
                    messages.success(request, "Saque realizado com sucesso!")
                    sacou = True
                # O saldo é insuficiente mas possui limite no limite_especial
                elif saldo + limite_especial >= valor_saque:
                    saldo_atualizado = (
                        saldo - valor_saque
                    )  # Fica negativo no limite do saldo+limite_especial
                    data_atual = datetime.now()
                    messages.warning(
                        request,
                        "Saque realizado com sucesso!\nUtilizando o limite especial da conta.",
                    )
                    sacou = True
                # Não possui saldo ou limite especial o suficiente
                # Não faz nada e re-renderiza a página
                else:
                    maximo_disponivel = saldo + limite_especial
                    messages.error(
                        request,
                        f"Saldo insuficiente. Seu saldo atual é de R${saldo:.2f} e seu limite especial é de R${limite_especial:.2f}.\nO máximo disponível para saque é de R${maximo_disponivel:.2f}.",
                    )

                if sacou:
                    try:
                        nova_movimentacao = Movimentacao.objects.create(
                            conta=dados_conta_cliente,
                            tipo_movimentacao=3,  # Saque
                            valor=valor_saque,
                            data_movimentacao=data_atual,
                        )

                        # Atualiza o saldo da conta no banco
                        dados_conta_cliente.saldo = saldo_atualizado
                        dados_conta_cliente.save()

                    except Exception as e:
                        # Não precisa redirecionar aqui pois está renderizando a página no final com a mensagem de erro
                        messages.error(request, f"Erro ao tentar realizar o saque: {e}")

        elif operacao == "transferencia":
            # Resgatar os valores do formulário
            valor_transferencia = formatar_valor(
                request.POST.get("valor_transferencia")
            )
            numero_conta_destino = request.POST.get("conta_destino_transferencia")

            if valor_transferencia <= Decimal("0.00"):
                messages.error(
                    request,
                    "Valor de transferência inválido.\nNão é possível realizar a transferência de R$ 0,00 reais.",
                )
            else:
                transferiu = False

                # Resgatar a conta de origem
                if not conta_selecionada_id:
                    conta_origem = Conta.objects.get(id_user=request.user.id)
                else:
                    conta_origem = Conta.objects.get(id=conta_selecionada_id)

                saldo_origem = Decimal(conta_origem.saldo)
                limite_especial = Decimal(conta_origem.limite_especial)

                # Verificar se a conta de destino existe
                conta_destino = Conta.objects.filter(
                    numero_conta=numero_conta_destino, ativa=True
                ).first()

                if not conta_destino:
                    messages.error(
                        request,
                        "Conta de destino não encontrada. Por favor, verifique o número da conta.",
                    )
                else:
                    # Possui saldo suficiente
                    if saldo_origem >= valor_transferencia:
                        # Atualizar saldo da conta de origem
                        saldo_origem_atualizado = saldo_origem - valor_transferencia
                        data_atual = datetime.now()
                        messages.success(request, "Saque realizado com sucesso!")

                        # Atualizar saldo da conta de destino
                        saldo_destino_atualizado = (
                            Decimal(conta_destino.saldo) + valor_transferencia
                        )
                        transferiu = True

                    # O saldo é insuficiente mas possui limite no limite_especial
                    elif saldo_origem + limite_especial >= valor_transferencia:
                        # Atualizar saldo na conta origem
                        saldo_origem_atualizado = (
                            saldo_origem - valor_transferencia
                        )  # Fica negativo no limite do saldo+limite_especial
                        data_atual = datetime.now()
                        messages.warning(
                            request,
                            "Transferência realizada com sucesso!\nUtilizando o limite especial da conta.",
                        )

                        # Atulizar saldo na conta destino
                        saldo_destino_atualizado = (
                            Decimal(conta_destino.saldo) + valor_transferencia
                        )
                        transferiu = True
                    # Não possui saldo ou limite especial o suficiente
                    # Não faz nada e re-renderiza a página com a mensagem
                    else:
                        maximo_disponivel = saldo_origem + limite_especial
                        messages.error(
                            request,
                            f"Saldo insuficiente. Seu saldo atual é de R${saldo_origem:.2f} e seu limite especial é de R${limite_especial:.2f}.\nO máximo disponível para saque é de R${maximo_disponivel:.2f}.",
                        )

                    if transferiu:
                        # Salvar a movimentação na conta de origem
                        try:
                            # ----------------- Conta de origem -------------
                            nova_movimentacao_origem = Movimentacao.objects.create(
                                conta=conta_origem,
                                tipo_movimentacao=4,  # Transferência enviada
                                valor=valor_transferencia,
                                data_movimentacao=data_atual,
                                conta_transferencia=conta_destino,
                            )

                            # Atualiza o saldo da conta no banco
                            conta_origem.saldo = saldo_origem_atualizado
                            conta_origem.save()

                            # ----------------- Conta de destino -------------
                            nova_movimentacao_destino = Movimentacao.objects.create(
                                conta=conta_destino,
                                tipo_movimentacao=5,  # Transferência recebida
                                valor=valor_transferencia,
                                data_movimentacao=data_atual,
                                conta_transferencia=conta_origem,
                            )

                            # Atualiza o saldo da conta no banco
                            conta_destino.saldo = saldo_destino_atualizado
                            conta_destino.save()

                        except Exception as e:
                            # Não precisa redirecionar aqui pois está renderizando a página no final com a mensagem de erro
                            messages.error(
                                request, f"Erro ao tentar realizar a transferência: {e}"
                            )

        # -----------------------------------------------------------------------------------
        # Após salvar (success) ou não (fail), recarrega a página com a mensagem:
        # Obter os dados atualizados para envio para o template
        # Só pega esses dados da conta pelo usuário logado, se não tiver sido passado
        # a conta na sessão pelo selecionar_conta
        if not conta_selecionada_id:
            dados_conta_cliente = Conta.objects.get(id_user=request.user.id)
        else:
            dados_conta_cliente = Conta.objects.get(id=conta_selecionada_id)
        # dados_conta_cliente = Conta.objects.get(id_user=request.user.id)
        dados_cliente = User.objects.get(id=request.user.id)
        # Apesar as últimas 3 movimentações da conta
        dados_movimentacoes = Movimentacao.objects.filter(
            conta=dados_conta_cliente
        ).order_by("-data_movimentacao")[:3]
        tipo_movimentacao_choices = Movimentacao.TIPO_MOVIMENTACAO_CHOICES
        tipo_conta_choices = Conta.TIPO_CONTA_CHOICES

        # Fetch com INNER JOIN de contas e user se as contas estiverem ativas
        contas_users = (
            Conta.objects.select_related("id_user")
            .values(
                "numero_conta",
                "tipo_conta",
                "id_user__first_name",
                "id_user__last_name",
            )
            .filter(ativa=True)
        )

        # Redirecionar para o conta_cliente com os dados de contexto atualizados
        return render(
            request,
            "conta_cliente.html",
            {
                "dados_conta_cliente": dados_conta_cliente,
                "dados_cliente": dados_cliente,
                "dados_movimentacoes": dados_movimentacoes,
                "tipo_movimentacao_choices": tipo_movimentacao_choices,
                "contas_users": contas_users,
                "tipo_conta_choices": tipo_conta_choices,
            },
        )


@login_required(login_url="/usuarios/logar")
def extrato(request, numero_conta):

    # Via link ou direto no navegador
    # Recupera a conta com base no número da conta
    dados_conta_cliente = get_object_or_404(Conta, numero_conta=numero_conta)
    # Recupera o usuário associado à conta
    dados_cliente = dados_conta_cliente.id_user
    tipo_movimentacao_choices = Movimentacao.TIPO_MOVIMENTACAO_CHOICES

    # Para vizualização dos filtros aplicados no momento
    periodo_aplicado = "Todo o período"
    tipo_aplicado = "Todos"

    # Resgata as movimentacoes para calculo do saldo médio e calcula
    movimentacoes_saldo_medio = Movimentacao.objects.filter(
        conta=dados_conta_cliente
    ).order_by("-data_movimentacao")
    saldo_medio = calcular_saldo_medio(movimentacoes_saldo_medio)

    # Via link ou direto no navegador
    if request.method == "GET":
        # Busca todas as movimentações associadas à conta
        # dados_movimentacoes = Movimentacao.objects.filter(conta=dados_conta_cliente)
        dados_movimentacoes = Movimentacao.objects.filter(
            conta=dados_conta_cliente
        ).order_by("-data_movimentacao")

        # Conta o número de movimentações
        numero_de_movimentacoes = dados_movimentacoes.count()

    elif request.method == "POST":
        # Recupera os valores do formulário
        periodo = request.POST.get("periodo")
        tipo_movimentacao = request.POST.get("tipo")

        # Filtra as movimentações com base no período selecionado
        if periodo == "5min":
            tempo_inicio = datetime.now() - timedelta(minutes=5)
            periodo_aplicado = "Últimos 5 minutos"
        elif periodo == "30min":
            tempo_inicio = datetime.now() - timedelta(minutes=30)
            periodo_aplicado = "Últimos 30 minutos"
        elif periodo == "2h":
            tempo_inicio = datetime.now() - timedelta(hours=2)
            periodo_aplicado = "Últimas 2 horas"
        elif periodo == "5h":
            tempo_inicio = datetime.now() - timedelta(hours=5)
            periodo_aplicado = "Últimas 5 horas"
        elif periodo == "24h":
            tempo_inicio = datetime.now() - timedelta(hours=24)
            periodo_aplicado = "Últimas 24 horas"
        elif periodo == "2d":
            tempo_inicio = datetime.now() - timedelta(days=2)
            periodo_aplicado = "Últimos 2 dias"
        elif periodo == "5d":
            tempo_inicio = datetime.now() - timedelta(days=5)
            periodo_aplicado = "Últimos 5 dias"
        else:
            # Todo o período
            tempo_inicio = None
            periodo_aplicado = "Todo o período"

        # Filtro base
        filtros = {"conta": dados_conta_cliente}

        # Aplica o filtro de período
        if tempo_inicio:
            # Sufixo __gte no Django ORM significa "greater than or equal to"
            filtros["data_movimentacao__gte"] = tempo_inicio

        # Aplica o filtro de tipo de movimentação, se não for "todos"
        if tipo_movimentacao and tipo_movimentacao != "todos":
            filtros["tipo_movimentacao"] = tipo_movimentacao
            tipo_aplicado = dict(tipo_movimentacao_choices).get(
                int(tipo_movimentacao), "Todos"
            )

        # print(f"\n\nFiltros aplicados: {filtros}\n\n")
        # Filtros aplicados: {'conta': <Conta: Id do usuário: admin - Número da conta: 626013 - Saldo: 1500.00>, 'tipo_movimentacao': '2'}

        # Recupera as movimentações filtradas
        dados_movimentacoes = Movimentacao.objects.filter(**filtros).order_by(
            "-data_movimentacao"
        )

        numero_de_movimentacoes = dados_movimentacoes.count()

    # Renderiza a página com GET ou POST
    return render(
        request,
        "extrato.html",
        {
            "dados_conta_cliente": dados_conta_cliente,
            "dados_movimentacoes": dados_movimentacoes,
            "dados_cliente": dados_cliente,
            "tipo_movimentacao_choices": tipo_movimentacao_choices,
            "numero_de_movimentacoes": numero_de_movimentacoes,
            "periodo_aplicado": periodo_aplicado,
            "tipo_aplicado": tipo_aplicado,
            "saldo_medio": saldo_medio,
        },
    )


@login_required(login_url="/usuarios/logar")
def listar_contas(request):

    if not request.user.is_superuser:
        messages.warning(
            request, "Acesso negado, somente Gerentes podem listar contas."
        )
        return redirect("conta_cliente")

    # Via link ou direto no navegador
    if request.method == "GET":

        # Pega do models os tipos de contas e os dados para preencher no select, caso alterado já altera no form automaticamente
        dados_contas = Conta.objects.all().order_by("id_user_id")
        TIPO_CONTA_CHOICES = Conta.TIPO_CONTA_CHOICES

        return render(
            request,
            "listar_contas.html",
            {
                "dados_contas": dados_contas,
                "tipo_conta_choices": TIPO_CONTA_CHOICES,
            },
        )

    return render(request, "listar_contas.html")


@login_required(login_url="/usuarios/logar")
def encerrar_conta(request, numero_conta):
    """
    Desativa a conta especificada pelo número, se estiver ativa.
    """

    if not request.user.is_superuser:
        messages.warning(
            request, "Acesso negado, somente Gerentes podem editar contas."
        )
        return redirect("conta_cliente")

    conta = get_object_or_404(Conta, numero_conta=numero_conta)

    if conta.saldo != 0:
        messages.error(
            request,
            "Não é possível encerrar a conta pois o saldo não está zerado.",
        )
        return redirect("listar_contas")

    if conta.ativa:
        conta.ativa = False
        conta.save()
        messages.success(request, "Conta desativada com sucesso.")
    else:
        messages.info(request, "A conta já está desativada.")

    return redirect("listar_contas")


@login_required(login_url="/usuarios/logar")
def ativar_conta(request, numero_conta):
    """
    Ativa a conta especificada pelo número, se estiver desativada.
    """

    if not request.user.is_superuser:
        messages.warning(
            request, "Acesso negado, somente Gerentes podem ativar contas."
        )
        return redirect("conta_cliente")

    # Obtém a conta a ser ativada
    conta = get_object_or_404(Conta, numero_conta=numero_conta)

    # Verifica se a conta já está ativa
    if conta.ativa:
        messages.info(request, "A conta já está ativa.")
        return redirect("listar_contas")

    # Verifica se o usuário já possui 2 contas ativas
    contas_ativas = Conta.objects.filter(id_user=conta.id_user, ativa=True)
    if contas_ativas.count() >= 2:
        messages.error(
            request, "O usuário já possui 2 contas ativas e não pode ativar outra."
        )
        return redirect("listar_contas")

    # Verifica se o usuário já possui uma conta ativa do mesmo tipo
    if contas_ativas.filter(tipo_conta=conta.tipo_conta).exists():
        messages.error(
            request,
            f"O usuário já possui uma conta do tipo {conta.get_tipo_conta_display()} ativa.",
        )
        return redirect("listar_contas")

    # Ativa a conta
    conta.ativa = True
    conta.save()
    messages.success(request, "Conta ativada com sucesso.")

    return redirect("listar_contas")


@login_required
def selecionar_conta(request):
    if request.method == "POST":
        conta_id = request.POST.get("conta")
        if conta_id:
            try:
                conta_selecionada = Conta.objects.get(id=conta_id)
                # Armazena a ID da conta selecionada na sessão
                request.session["conta_selecionada"] = conta_id
                # Redireciona para a página conta_cliente
                return redirect("conta_cliente")
            except Conta.DoesNotExist:
                # Lida com a exceção caso a conta não seja encontrada
                return render(
                    request,
                    "selecionar_conta.html",
                    {
                        "mensagem": "Conta não encontrada.",
                        "contas_ativas": Conta.objects.filter(
                            id_user=request.user, ativa=True
                        ),
                    },
                )

    # Se o método não for POST, ou se algo der errado, renderiza o formulário
    contas_ativas = Conta.objects.filter(id_user=request.user, ativa=True)
    return render(request, "selecionar_conta.html", {"contas_ativas": contas_ativas})
