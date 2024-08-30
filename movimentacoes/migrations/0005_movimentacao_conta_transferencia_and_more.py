# Generated by Django 5.1 on 2024-08-30 10:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0003_remove_conta_nome_conta_id_user'),
        ('movimentacoes', '0004_movimentacao_saldo_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimentacao',
            name='conta_transferencia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movimentacoes_transferidas', to='contas.conta'),
        ),
        migrations.AlterField(
            model_name='movimentacao',
            name='conta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimentacoes', to='contas.conta'),
        ),
        migrations.AlterField(
            model_name='movimentacao',
            name='tipo_movimentacao',
            field=models.IntegerField(choices=[(1, 'Abertura de Conta'), (2, 'Depósito'), (3, 'Saque'), (4, 'Transferência enviada'), (5, 'Transferência recebida'), (6, 'Encerramento de Conta')]),
        ),
    ]
