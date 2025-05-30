import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Supplier, GoodsReceipt, GoodsReceiptItem, SupplierOrderItem
from parts.models import Part, Manufacturer


class Command(BaseCommand):
    help = 'Импортирует приходную накладную из Excel-файла'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к Excel-файлу')
        parser.add_argument('supplier_id', type=int, help='ID поставщика')
        parser.add_argument('receipt_id', type=int, help='ID приходной накладной')

    def handle(self, *args, **options):
        file_path = options['file_path']
        supplier_id = options['supplier_id']
        receipt_id = options['receipt_id']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
            return

        # try:
        # Читаем Excel-файл
        df = pd.read_excel(file_path)

        # Проверяем обязательные колонки
        required_columns = ['part_number', 'part_name', 'manufacturer_name', 'quantity', 'price']
        if not all(col in df.columns for col in required_columns):
            self.stdout.write(self.style.ERROR(
                f'Файл должен содержать колонки: {", ".join(required_columns)}'
            ))
            return

        # Получаем поставщика
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Поставщик с ID {supplier_id} не найден'))
            return

        # Создаем приходную накладную
        receipt = GoodsReceipt.objects.get(id=receipt_id)
        receipt.notes = f"Импортировано из файла {os.path.basename(file_path)}"

        supplier_order = receipt.supplier_order

        # Обрабатываем каждую строку
        total_amount = 0
        for index, row in df.iterrows():
            part_number = str(row['part_number']).strip()
            part_name = str(row['part_name']).strip()
            quantity = int(row['quantity'])
            price = int(row['price'])
            manufacturer_name = str(row['manufacturer_name']).strip()

            manufacturer, created = Manufacturer.objects.get_or_create(
                name=manufacturer_name,
            )

            # Ищем деталь по номеру или создаем новую
            part, created = Part.objects.get_or_create(
                original_number=part_number,
                defaults={
                    'name': part_name,
                    'category': self.get_default_category(),
                    'manufacturer': manufacturer,
                },
            )

            try:
                supplier_order_item = SupplierOrderItem.objects.get(
                    supplier_order=supplier_order,
                    part=part,
                )
                # Создаем позицию в накладной
                GoodsReceiptItem.objects.create(
                    receipt=receipt,
                    supplier_order_item=supplier_order_item,
                    quantity_received=quantity,
                    price=price,
                    part=part,
                )

                total_amount += quantity * price
            except SupplierOrderItem.DoesNotExist:
                GoodsReceiptItem.objects.create(
                    receipt=receipt,
                    supplier_order_item=None,
                    quantity_received=quantity,
                    price=price,
                    part=part,
                )

                total_amount += quantity * price

        # Обновляем общую сумму накладной
        receipt.total_amount = total_amount
        receipt.save()

        self.stdout.write(self.style.SUCCESS(
            f'Успешно импортирована накладная #{receipt.id} для {supplier.name}. '
            f'Импортировано {len(df)} позиций, общая сумма: {total_amount:.2f} руб.'
        ))

        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'Ошибка импорта: {str(e)}'))
        #     # Удаляем частично созданную накладную при ошибке
        #     if 'receipt' in locals():
        #         receipt.delete()

    def get_default_category(self):
        """Возвращает категорию по умолчанию"""
        from parts.models import PartCategory
        category, _ = PartCategory.objects.get_or_create(
            name='Импортированные'
        )
        return category