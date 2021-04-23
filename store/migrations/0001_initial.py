# Generated by Django 3.2 on 2021-04-22 21:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Good',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Good',
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(verbose_name='Price')),
                ('good', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='store.good', verbose_name='Good')),
            ],
            options={
                'verbose_name': 'Purchase',
                'unique_together': {('good', 'price')},
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, max_length=254, verbose_name='E-Mail')),
                ('status', models.TextField(choices=[('DR', 'Draft'), ('PR', 'Processing'), ('CA', 'Canceled'), ('FI', 'Finished')], max_length=2)),
                ('purchases', models.ManyToManyField(related_name='orders', to='store.Purchase')),
                ('user', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Buyer')),
            ],
            options={
                'verbose_name': 'Order',
                'permissions': [('view_my_order', 'View my orders'), ('moderate_my_order', 'Moderate my orders')],
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(verbose_name='Price')),
                ('good', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='store.good', verbose_name='Good')),
            ],
            options={
                'verbose_name': 'Offer',
            },
        ),
    ]
