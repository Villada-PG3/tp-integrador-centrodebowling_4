# Generated by Django 5.1 on 2024-09-16 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_estadopartida_estadopedido_estadoreserva_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='mail',
            field=models.EmailField(max_length=60),
        ),
    ]