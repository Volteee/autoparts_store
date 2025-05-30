import os
import openpyxl
from django.core.management.base import BaseCommand
from django.conf import settings
from dealers.models import Dealer, DealerStockNorm
from parts.models import Part


class Command(BaseCommand):
    help = 'Обрабатывает Excel-файлы от дилеров и обновляет текущие запасы'

    def handle(self, *args, **options):
        # Директория с файлами от дилеров
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'dealer_uploads')

        if not os.path.exists(upload_dir):
            self.stdout.write(self.style.WARNING(f"Директория {upload_dir} не существует"))
            return

        processed_count = 0
        for file_name in os.listdir(upload_dir):
            if not file_name.endswith('.xlsx'):
                continue

            file_path = os.path.join(upload_dir, file_name)

            # Извлекаем ID дилера из имени файла
            try:
                dealer_id = int(file_name.split('_')[1])
                dealer = Dealer.objects.get(id=dealer_id)
            except (ValueError, IndexError, Dealer.DoesNotExist):
                self.stdout.write(self.style.ERROR(f"Неверный формат имени файла или дилер не найден: {file_name}"))
                continue

            try:
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active

                updated_items = 0
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not row or not row[0]:
                        continue

                    part_number = str(row[0]).strip()
                    try:
                        current_stock = int(row[3]) if row[3] is not None else 0
                    except (TypeError, ValueError):
                        current_stock = 0

                    try:
                        # Ищем деталь по оригинальному номеру
                        part = Part.objects.get(original_number=part_number)

                        # Обновляем запись о запасе
                        stock_norm, created = DealerStockNorm.objects.update_or_create(
                            dealer=dealer,
                            part=part,
                            defaults={'current_stock': current_stock}
                        )
                        updated_items += 1
                    except Part.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Деталь с номером {part_number} не найдена"))

                # Перемещаем обработанный файл
                processed_dir = os.path.join(settings.MEDIA_ROOT, 'dealer_uploads', 'processed')
                os.makedirs(processed_dir, exist_ok=True)
                os.rename(file_path, os.path.join(processed_dir, file_name))

                self.stdout.write(self.style.SUCCESS(
                    f"Обработан файл {file_name} для дилера {dealer}. Обновлено позиций: {updated_items}"
                ))
                processed_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Ошибка обработки файла {file_name}: {str(e)}"
                ))

        self.stdout.write(self.style.SUCCESS(f"Обработано файлов: {processed_count}"))