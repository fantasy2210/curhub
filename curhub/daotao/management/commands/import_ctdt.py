import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from daotao.models import ChuongTrinhDaoTao, NganhDaoTao

class Command(BaseCommand):
    help = 'Imports training programs from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import.')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # Expected columns based on the image:
                # 'Mã ngành', 'Tên ngành', 'Chương trình đào tạo (CQ)', 'số QĐ ban hành (CQ)', 'Ghi chú'
                
                # Map CSV headers to internal names for easier access
                column_mapping = {
                    'Mã ngành': 'ma_nganh_csv',
                    'Tên ngành': 'ten_nganh_csv',
                    'Chương trình đào tạo (CQ)': 'ten_chuong_trinh_dao_tao_cq',
                    'số QĐ ban hành (CQ)': 'so_qd_ban_hanh_cq',
                    'Ghi chú': 'ghi_chu_csv',
                }

                # Check if all expected columns are present
                missing_columns = [col for original, col in column_mapping.items() if original not in reader.fieldnames]
                if missing_columns:
                    raise CommandError(f"Missing required columns in CSV: {', '.join(missing_columns)}")

                self.stdout.write(self.style.SUCCESS(f"Starting import from {csv_file_path}..."))
                
                imported_count = 0
                updated_count = 0
                skipped_count = 0

                for row in reader:
                    # Rename keys based on mapping
                    mapped_row = {column_mapping.get(key, key): value for key, value in row.items()}

                    ma_nganh_ctdt = mapped_row.get('ma_nganh_csv')
                    ten_nganh_ctdt = mapped_row.get('ten_chuong_trinh_dao_tao_cq')
                    ten_nganh_chung = mapped_row.get('ten_nganh_csv')
                    so_qd_ban_hanh_cq = mapped_row.get('so_qd_ban_hanh_cq', '').strip()
                    ghi_chu_csv = mapped_row.get('ghi_chu_csv', '').strip()

                    if not ma_nganh_ctdt or not ten_nganh_ctdt:
                        self.stdout.write(self.style.WARNING(f"Skipping row due to missing 'Mã ngành' or 'Chương trình đào tạo (CQ)': {row}"))
                        skipped_count += 1
                        continue

                    # Handle NganhDaoTao (nganh_hoc_chung)
                    nganh_hoc_chung_obj = None
                    if ten_nganh_chung:
                        nganh_hoc_chung_obj, created = NganhDaoTao.objects.get_or_create(
                            ten_nganh=ten_nganh_chung,
                            defaults={'ma_nganh': ten_nganh_chung.replace(' ', '').upper()[:20]} # Simple unique code
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Created new NganhDaoTao: {nganh_hoc_chung_obj.ten_nganh}"))

                    # Parse 'số QĐ ban hành (CQ)'
                    so_quyet_dinh = None
                    ngay_ban_hanh = None
                    if so_qd_ban_hanh_cq:
                        parts = so_qd_ban_hanh_cq.split(',')
                        if len(parts) == 2:
                            so_quyet_dinh = parts[0].strip()
                            date_str = parts[1].strip()
                            try:
                                # Assuming date format DD/MM/YYYY
                                ngay_ban_hanh = datetime.strptime(date_str, '%d/%m/%Y').date()
                            except ValueError:
                                self.stdout.write(self.style.WARNING(f"Could not parse date '{date_str}' for {ma_nganh_ctdt}. Skipping date import."))
                        else:
                            self.stdout.write(self.style.WARNING(f"Unexpected format for 'số QĐ ban hành (CQ)' for {ma_nganh_ctdt}: '{so_qd_ban_hanh_cq}'. Storing as is in so_quyet_dinh_ban_hanh."))
                            so_quyet_dinh = so_qd_ban_hanh_cq # Store the whole string if format is unexpected

                    # Determine trinh_do_dao_tao and ghi_chu_ctdt
                    trinh_do = 'DH' # Default to Đại học
                    final_ghi_chu = ghi_chu_csv

                    if 'Cao đẳng' in ghi_chu_csv:
                        trinh_do = 'CD'
                        final_ghi_chu = ghi_chu_csv.replace('Cao đẳng', '').strip()
                    
                    # If 'Co-op' is in ghi_chu_csv, it will be stored in ghi_chu_ctdt
                    # No direct mapping to hinh_thuc_dao_tao as it's not a standard choice.

                    # Create or update ChuongTrinhDaoTao
                    ctdt, created = ChuongTrinhDaoTao.objects.update_or_create(
                        ma_nganh_ctdt=ma_nganh_ctdt,
                        defaults={
                            'ten_nganh_ctdt': ten_nganh_ctdt,
                            'nganh_hoc_chung': nganh_hoc_chung_obj,
                            'trinh_do_dao_tao': trinh_do,
                            'so_quyet_dinh_ban_hanh': so_quyet_dinh,
                            'ngay_ban_hanh_qd': ngay_ban_hanh,
                            'ghi_chu_ctdt': final_ghi_chu,
                            # Add other fields if they are in your CSV and need mapping
                        }
                    )

                    if created:
                        imported_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Successfully imported: {ctdt.ten_nganh_ctdt} ({ctdt.ma_nganh_ctdt})"))
                    else:
                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Successfully updated: {ctdt.ten_nganh_ctdt} ({ctdt.ma_nganh_ctdt})"))

                self.stdout.write(self.style.SUCCESS(f"\nImport complete!"))
                self.stdout.write(self.style.SUCCESS(f"Total imported: {imported_count}"))
                self.stdout.write(self.style.SUCCESS(f"Total updated: {updated_count}"))
                self.stdout.write(self.style.WARNING(f"Total skipped: {skipped_count}"))

        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist.')
        except Exception as e:
            raise CommandError(f'An error occurred during import: {e}')
