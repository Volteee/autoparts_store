# Generated by Django 5.2.1 on 2025-05-30 05:41

import django.db.models.deletion
import parts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название производителя')),
            ],
            options={
                'verbose_name': 'Производитель',
                'verbose_name_plural': 'Производители',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название поставщика')),
                ('contact_info', models.TextField(blank=True, verbose_name='Контактная информация')),
            ],
            options={
                'verbose_name': 'Поставщик',
                'verbose_name_plural': 'Поставщики',
            },
        ),
        migrations.CreateModel(
            name='PartCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название категории')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='parts.partcategory', verbose_name='Родительская категория')),
            ],
            options={
                'verbose_name': 'Категория запчастей',
                'verbose_name_plural': 'Категории запчастей',
            },
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название детали')),
                ('original_number', models.CharField(blank=True, max_length=50, verbose_name='Оригинальный номер')),
                ('location', models.CharField(blank=True, choices=[('left', 'Левый'), ('right', 'Правый'), ('front', 'Передний'), ('rear', 'Задний'), ('1', '1-й'), ('2', '2-й'), ('3', '3-й'), ('4', '4-й')], max_length=20, verbose_name='Расположение')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('synonyms', models.TextField(blank=True, help_text='Разделяйте названия запятыми', verbose_name='Синонимы/Сленговые названия')),
                ('manufacturer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', to='parts.manufacturer', verbose_name='Производитель')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', to='parts.partcategory', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Запчасть',
                'verbose_name_plural': 'Запчасти',
                'unique_together': {('name', 'manufacturer', 'location')},
            },
        ),
        migrations.CreateModel(
            name='PriceList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=parts.models.price_list_upload_path, verbose_name='Файл прайс-листа')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')),
                ('is_active', models.BooleanField(default=True, verbose_name='Актуален')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_lists', to='parts.supplier', verbose_name='Поставщик')),
            ],
            options={
                'verbose_name': 'Прайс-лист',
                'verbose_name_plural': 'Прайс-листы',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='DeliveryOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_range', models.CharField(choices=[('3-5', '3-5 дней'), ('6-10', '6-10 дней'), ('10-20', '10-20 дней')], max_length=10, verbose_name='Срок доставки')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена с доставкой')),
                ('in_stock', models.PositiveIntegerField(default=0, verbose_name='Количество на складе')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_options', to='parts.part', verbose_name='Деталь')),
                ('price_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_options', to='parts.pricelist', verbose_name='Прайс-лист')),
            ],
            options={
                'verbose_name': 'Вариант поставки',
                'verbose_name_plural': 'Варианты поставки',
                'unique_together': {('price_list', 'part', 'delivery_range')},
            },
        ),
    ]
