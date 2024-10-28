# Generated by Django 5.1 on 2024-09-02 11:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id_cliente', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=60)),
                ('direccion', models.CharField(max_length=120)),
                ('telefono', models.CharField(max_length=20)),
                ('mail', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='EstadoPartida',
            fields=[
                ('estado', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=240)),
            ],
        ),
        migrations.CreateModel(
            name='EstadoPedido',
            fields=[
                ('estado', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=240)),
            ],
        ),
        migrations.CreateModel(
            name='EstadoPista',
            fields=[
                ('estado', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=240)),
            ],
        ),
        migrations.CreateModel(
            name='EstadoReserva',
            fields=[
                ('estado', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=240)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id_producto', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=60)),
                ('descripcion', models.CharField(max_length=240)),
                ('precio', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Partida',
            fields=[
                ('id_partida', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.estadopartida')),
            ],
        ),
        migrations.CreateModel(
            name='Jugador',
            fields=[
                ('id_jugador', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_jugador', models.CharField(max_length=10)),
                ('orden', models.IntegerField()),
                ('id_partida', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.partida')),
            ],
            options={
                'unique_together': {('id_jugador', 'id_partida')},
            },
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id_pedido', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_hora_pedido', models.DateField()),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.estadopedido')),
                ('id_producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.producto')),
            ],
        ),
        migrations.CreateModel(
            name='PistaBowling',
            fields=[
                ('id_pista', models.AutoField(primary_key=True, serialize=False)),
                ('capacidad_maxima', models.IntegerField()),
                ('descripcion', models.CharField(max_length=240)),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.estadopista')),
            ],
        ),
        migrations.AddField(
            model_name='partida',
            name='id_pista',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.pistabowling'),
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id_reserva', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_hora_reserva', models.DateField()),
                ('estado', models.CharField(max_length=20)),
                ('id_cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.cliente')),
                ('id_partida', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.partida')),
                ('id_pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.pedido')),
                ('id_pista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.pistabowling')),
            ],
        ),
        migrations.AddField(
            model_name='partida',
            name='id_reserva',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.reserva'),
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('numero_turno', models.AutoField(primary_key=True, serialize=False)),
                ('orden', models.CharField(max_length=20)),
                ('ultimo_turno', models.BooleanField()),
                ('id_partida', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.partida')),
            ],
        ),
        migrations.CreateModel(
            name='Tirada',
            fields=[
                ('numero_tirada', models.AutoField(primary_key=True, serialize=False)),
                ('pinos_deribados', models.IntegerField()),
                ('orden', models.IntegerField()),
                ('id_jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.jugador')),
                ('numero_turno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.turno')),
            ],
        ),
        migrations.CreateModel(
            name='PedidoXProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('id_pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.pedido')),
                ('id_producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.producto')),
            ],
            options={
                'unique_together': {('id_pedido', 'id_producto')},
            },
        ),
        migrations.CreateModel(
            name='HistorialEstado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora_inicio', models.DateField()),
                ('fecha_hora_fin', models.DateField()),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.estadoreserva')),
                ('id_reserva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.reserva')),
            ],
            options={
                'unique_together': {('id_reserva', 'estado')},
            },
        ),
    ]