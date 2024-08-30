from django.db import models
from contas.models import Conta
from decimal import Decimal
from django.db.models import Avg


class Movimentacao(models.Model):
    TIPO_MOVIMENTACAO_CHOICES = [
        (1, "Abertura de Conta"),
        (2, "Depósito"),
        (3, "Saque"),
        (4, "Transferência enviada"),
        (5, "Transferência recebida"),
        (6, "Encerramento de Conta"),
    ]

    data_movimentacao = models.DateTimeField(auto_now_add=True)
    tipo_movimentacao = models.IntegerField(choices=TIPO_MOVIMENTACAO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    conta = models.ForeignKey(
        Conta, on_delete=models.CASCADE, related_name="movimentacoes"
    )
    saldo_antes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_apos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_media = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conta_transferencia = models.ForeignKey(
        Conta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes_transferidas",
    )

    def __str__(self):
        tipo_movimentacao_display = self.get_tipo_movimentacao_display()
        return f"{tipo_movimentacao_display} de R${self.valor} em {self.data_movimentacao.strftime('%d/%m/%Y %H:%M:%S')}"

    def save(self, *args, **kwargs):
        if self.tipo_movimentacao == 1:  # Abertura de Conta
            # Para abertura de conta, o saldo_antes deve ser o saldo da última movimentação ou 0 se for a primeira movimentação
            if (
                not self.pk
            ):  # Apenas define saldo_antes e saldo_apos se a movimentação for nova
                ultima_movimentacao = (
                    Movimentacao.objects.filter(conta=self.conta)
                    .order_by("-data_movimentacao")
                    .first()
                )
                if ultima_movimentacao:
                    self.saldo_antes = ultima_movimentacao.saldo_apos
                else:
                    self.saldo_antes = Decimal("0.00")

            self.saldo_apos = (
                self.valor
            )  # O saldo_apos é igual ao valor da movimentação

        elif self.tipo_movimentacao == 6:  # Encerramento de Conta
            ultima_movimentacao = (
                Movimentacao.objects.filter(conta=self.conta)
                .order_by("-data_movimentacao")
                .first()
            )
            if ultima_movimentacao:
                self.saldo_antes = ultima_movimentacao.saldo_apos
            else:
                self.saldo_antes = Decimal("0.00")
            self.saldo_apos = Decimal("0.00")  # O saldo_apos é 0 para encerramento

        else:
            # Para outros tipos de movimentação, o saldo_antes deve ser calculado com base na última movimentação
            ultima_movimentacao = (
                Movimentacao.objects.filter(conta=self.conta)
                .order_by("-data_movimentacao")
                .first()
            )
            if ultima_movimentacao:
                self.saldo_antes = ultima_movimentacao.saldo_apos
            else:
                self.saldo_antes = Decimal("0.00")

            # Calcula o saldo_apos com base no tipo de movimentação
            if self.tipo_movimentacao == 2:  # Depósito
                self.saldo_apos = self.saldo_antes + self.valor
            elif self.tipo_movimentacao == 3:  # Saque
                self.saldo_apos = self.saldo_antes - self.valor
            elif self.tipo_movimentacao == 4:  # Transferência enviada
                self.saldo_apos = self.saldo_antes - self.valor
            elif self.tipo_movimentacao == 5:  # Transferência recebida
                self.saldo_apos = self.saldo_antes + self.valor

        super().save(*args, **kwargs)

        # Recalcular o saldo médio após a salva
        self.recalcular_saldo_medio()

    def recalcular_saldo_medio(self):
        # Calcula o saldo médio da conta
        saldo_medio = Movimentacao.objects.filter(conta=self.conta).aggregate(
            media_saldo_antes=Avg("saldo_antes"), media_saldo_apos=Avg("saldo_apos")
        )

        media_saldo_antes = saldo_medio.get("media_saldo_antes", Decimal("0.00"))
        media_saldo_apos = saldo_medio.get("media_saldo_apos", Decimal("0.00"))

        saldo_media = (media_saldo_antes + media_saldo_apos) / 2

        # Atualiza apenas o campo saldo_media para evitar loops de salvamento
        Movimentacao.objects.filter(pk=self.pk).update(saldo_media=saldo_media)


# from django.db import models
# from contas.models import Conta
# from decimal import Decimal
# from django.db.models import Avg


# class Movimentacao(models.Model):
#     TIPO_MOVIMENTACAO_CHOICES = [
#         (1, "Abertura de Conta"),
#         (2, "Depósito"),
#         (3, "Saque"),
#         (4, "Transferência"),
#         (5, "Encerramento de Conta"),
#     ]

#     data_movimentacao = models.DateTimeField(auto_now_add=True)
#     tipo_movimentacao = models.IntegerField(choices=TIPO_MOVIMENTACAO_CHOICES)
#     valor = models.DecimalField(max_digits=10, decimal_places=2)
#     conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
#     saldo_antes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     saldo_apos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     saldo_media = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     def __str__(self):
#         tipo_movimentacao_display = self.get_tipo_movimentacao_display()
#         return f"{tipo_movimentacao_display} de R${self.valor} em {self.data_movimentacao.strftime('%d/%m/%Y %H:%M:%S')}"

#     def save(self, *args, **kwargs):
#         if self.tipo_movimentacao == 1:  # Abertura de Conta
#             # Para abertura de conta, o saldo_antes deve ser o saldo da última movimentação ou 0 se for a primeira movimentação
#             if (
#                 not self.pk
#             ):  # Apenas define saldo_antes e saldo_apos se a movimentação for nova
#                 ultima_movimentacao = (
#                     Movimentacao.objects.filter(conta=self.conta)
#                     .order_by("-data_movimentacao")
#                     .first()
#                 )
#                 if ultima_movimentacao:
#                     self.saldo_antes = ultima_movimentacao.saldo_apos
#                 else:
#                     self.saldo_antes = Decimal("0.00")

#             self.saldo_apos = (
#                 self.valor
#             )  # O saldo_apos é igual ao valor da movimentação

#         elif self.tipo_movimentacao == 5:  # Encerramento de Conta
#             ultima_movimentacao = (
#                 Movimentacao.objects.filter(conta=self.conta)
#                 .order_by("-data_movimentacao")
#                 .first()
#             )
#             if ultima_movimentacao:
#                 self.saldo_antes = ultima_movimentacao.saldo_apos
#             else:
#                 self.saldo_antes = Decimal("0.00")
#             self.saldo_apos = Decimal("0.00")  # O saldo_apos é 0 para encerramento

#         else:
#             # Para outros tipos de movimentação, o saldo_antes deve ser calculado com base na última movimentação
#             ultima_movimentacao = (
#                 Movimentacao.objects.filter(conta=self.conta)
#                 .order_by("-data_movimentacao")
#                 .first()
#             )
#             if ultima_movimentacao:
#                 self.saldo_antes = ultima_movimentacao.saldo_apos
#             else:
#                 self.saldo_antes = Decimal("0.00")

#             # Calcula o saldo_apos com base no tipo de movimentação
#             if self.tipo_movimentacao == 2:  # Depósito
#                 self.saldo_apos = self.saldo_antes + self.valor
#             elif self.tipo_movimentacao == 3:  # Saque
#                 self.saldo_apos = self.saldo_antes - self.valor
#             elif self.tipo_movimentacao == 4:  # Transferência
#                 self.saldo_apos = self.saldo_antes - self.valor

#         super().save(*args, **kwargs)

#         # Recalcular o saldo médio após a salva
#         self.recalcular_saldo_medio()

#     def recalcular_saldo_medio(self):
#         # Calcula o saldo médio da conta
#         saldo_medio = Movimentacao.objects.filter(conta=self.conta).aggregate(
#             media_saldo_antes=Avg("saldo_antes"), media_saldo_apos=Avg("saldo_apos")
#         )

#         media_saldo_antes = saldo_medio.get("media_saldo_antes", Decimal("0.00"))
#         media_saldo_apos = saldo_medio.get("media_saldo_apos", Decimal("0.00"))

#         saldo_media = (media_saldo_antes + media_saldo_apos) / 2

#         # Atualiza apenas o campo saldo_media para evitar loops de salvamento
#         Movimentacao.objects.filter(pk=self.pk).update(saldo_media=saldo_media)
