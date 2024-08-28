# Generated by Django 5.0.6 on 2024-08-24 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movimentacoes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimentacao',
            name='tipo_movimentacao',
            field=models.IntegerField(choices=[(1, 'Abertura de Conta'), (2, 'Depósito'), (3, 'Saque'), (4, 'Transferência'), (5, 'Encerramento de Conta')]),
        ),
    ]
