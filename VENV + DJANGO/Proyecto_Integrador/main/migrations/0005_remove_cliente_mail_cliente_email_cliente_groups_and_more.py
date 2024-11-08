# Generated by Django 5.1 on 2024-09-16 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('main', '0004_cliente_password_alter_cliente_mail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='mail',
        ),
        migrations.AddField(
            model_name='cliente',
            name='email',
            field=models.EmailField(default='default@example.com', max_length=254, unique=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cliente',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$870000$YfxfBibwpYoRi2d8itO3Sz$o8SVihynRJiXU0Kamt/gx3sD8hU7sqbEOPX8met5G88=', max_length=128),
        ),
    ]
