import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.utils import timezone
from parts.models import (
    PriceList, DeliveryOption, Part,
    Manufacturer, Supplier
)


class Command(BaseCommand):
    help = 'Импортирует прайс-лист из Excel-файла'

    def add_arguments(self, parser):
        parser.add_argument('supplier_id', type=int, help='ID поставщика')
        parser.add_argument('file_path', type=str, help='Путь к Excel-файлу')
        parser.add_argument('pricelist_id', type=str, help='ID прайс-листа')

    def handle(self, *args, **options):
        supplier_id = options['supplier_id']
        file_path = options['file_path']
        pricelist_id = options['pricelist_id']

        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Поставщик с ID {supplier_id} не найден'))
            return

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
            return

        try:
            # Читаем Excel-файл (пропускаем первые 9 строк)
            df = pd.read_excel(file_path, skiprows=9, header=None)

            # Проверяем количество столбцов
            if df.shape[1] < 7:
                self.stdout.write(self.style.ERROR(
                    'Файл должен содержать минимум 7 колонок начиная с 10 строки'
                ))
                return

            # Создаем новый прайс-лист
            pricelist = PriceList.objects.get(id=pricelist_id)

            # Обрабатываем каждую строку
            created_count = 0
            for index, row in df.iterrows():
                if row.isnull().all():
                    continue  # Пропускаем пустые строки

                # Извлекаем данные из строки
                original_number = str(row[0]).strip()
                manufacturer_name = str(row[1]).strip()
                part_name = str(row[2]).strip()
                price_3_5 = self.parse_float(row[3])
                price_6_10 = self.parse_float(row[4])
                price_10_20 = self.parse_float(row[5])
                in_stock = self.parse_int(row[6])

                # Пропускаем строки с отсутствующими обязательными данными
                if not original_number or not manufacturer_name or not part_name:
                    continue

                # Получаем или создаем производителя
                manufacturer, _ = Manufacturer.objects.get_or_create(
                    name=manufacturer_name
                )

                # Получаем или создаем деталь
                part, created = Part.objects.get_or_create(
                    original_number=original_number,
                    manufacturer=manufacturer,
                    defaults={
                        'name': part_name,
                        'category': self.get_default_category()
                    }
                )

                # Создаем варианты доставки
                if price_3_5:
                    DeliveryOption.objects.create(
                        price_list=pricelist,
                        part=part,
                        delivery_range='3-5',
                        price=price_3_5,
                        in_stock=in_stock
                    )
                    created_count += 1

                if price_6_10:
                    DeliveryOption.objects.create(
                        price_list=pricelist,
                        part=part,
                        delivery_range='6-10',
                        price=price_6_10,
                        in_stock=in_stock
                    )
                    created_count += 1

                if price_10_20:
                    DeliveryOption.objects.create(
                        price_list=pricelist,
                        part=part,
                        delivery_range='10-20',
                        price=price_10_20,
                        in_stock=in_stock
                    )
                    created_count += 1

            self.stdout.write(self.style.SUCCESS(
                f'Успешно импортирован прайс-лист для {supplier.name}. '
                f'Создано {created_count} вариантов поставки.'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка импорта: {str(e)}'))
            # Удаляем частично созданный прайс-лист при ошибке
            if 'pricelist' in locals():
                pricelist.delete()

    def parse_float(self, value):
        """Конвертирует значение в float, если возможно"""
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def parse_int(self, value):
        """Конвертирует значение в int, если возможно"""
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def get_default_category(self):
        """Возвращает категорию по умолчанию"""
        from parts.models import PartCategory
        category, _ = PartCategory.objects.get_or_create(
            name='Другое'
        )
        return category