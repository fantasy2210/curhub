import csv
from django.core.management.base import BaseCommand, CommandError
from daotao.models import HocPhan, ChuongTrinhDaoTao, ChiTietHocPhanTrongCTDT, NganhDaoTao, DonViDaoTao

class Command(BaseCommand):
    help = 'Imports course modules and their details within training programs from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import.')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # Expected columns from the provided CSV sample:
                # GhiChu1,LT,TH,BT,DA,LA,TN,TT,BTL,TUH,TTLT,TTTH,LMS,NHHK,DoiTuongSV,MaKhoi,MaBH,MaNgChng,ChuyenNganh,IDMH,MaMH,TenMH,SoTietMH,SoTinChi,TTCTDTTH,IsMHBB,IsMHTN
                
                # Validate required columns
                required_columns = ['MaMH', 'TenMH', 'SoTietMH', 'SoTinChi', 'MaKhoi', 'NHHK', 'IsMHBB', 'IsMHTN', 'LT', 'TH']
                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                if missing_columns:
                    raise CommandError(f"Missing required columns in CSV: {', '.join(missing_columns)}")

                self.stdout.write(self.style.SUCCESS(f"Starting import from {csv_file_path}..."))
                
                imported_hp_count = 0
                updated_hp_count = 0
                imported_ctdt_hp_count = 0
                updated_ctdt_hp_count = 0
                skipped_rows_count = 0

                for row in reader:
                    ma_hoc_phan = row.get('MaMH')
                    ten_hoc_phan = row.get('TenMH')
                    so_tiet_mh = row.get('SoTietMH')
                    so_tin_chi = row.get('SoTinChi')
                    ma_khoi_ctdt = row.get('MaKhoi') # This will be used as ma_nganh_ctdt
                    nhhk = row.get('NHHK')
                    is_mhbb = row.get('IsMHBB')
                    is_mhtn = row.get('IsMHTN')
                    lt_tiet = row.get('LT')
                    th_tiet = row.get('TH')
                    ghi_chu_1 = row.get('GhiChu1', '').strip()

                    if not all([ma_hoc_phan, ten_hoc_phan, so_tiet_mh, so_tin_chi, ma_khoi_ctdt, nhhk]):
                        self.stdout.write(self.style.WARNING(f"Skipping row due to missing critical data: {row}"))
                        skipped_rows_count += 1
                        continue

                    # --- 1. Handle HocPhan (Course Module) ---
                    try:
                        so_tiet_mh_int = int(so_tiet_mh)
                        so_tin_chi_int = int(so_tin_chi)
                        lt_tiet_int = int(lt_tiet) if lt_tiet else 0
                        th_tiet_int = int(th_tiet) if th_tiet else 0
                        is_mhtn_bool = bool(int(is_mhtn)) if is_mhtn else False # 1 for True, 0 for False
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f"Skipping row due to invalid number format for HocPhan fields: {row} - Error: {e}"))
                        skipped_rows_count += 1
                        continue

                    hoc_phan, created_hp = HocPhan.objects.update_or_create(
                        ma_hoc_phan=ma_hoc_phan,
                        defaults={
                            'ten_hoc_phan': ten_hoc_phan,
                            'tong_so_tin_chi_goc': so_tin_chi_int,
                            'so_tiet_tong_cong': so_tiet_mh_int,
                            'so_gio_ly_thuyet_goc': lt_tiet_int, # Assuming 1 tiet = 1 gio for simplicity
                            'so_gio_thuc_hanh_goc': th_tiet_int, # Assuming 1 tiet = 1 gio for simplicity
                            'la_hoc_phan_tu_chon': is_mhtn_bool,
                            # tin_chi_ly_thuyet_goc and tin_chi_thuc_hanh_goc are not directly in CSV,
                            # but can be derived if needed (e.g., from LT/TH and a conversion factor)
                            # For now, leaving them as default or requiring manual update if needed.
                        }
                    )
                    if created_hp:
                        imported_hp_count += 1
                        self.stdout.write(self.style.SUCCESS(f"  Created HocPhan: {hoc_phan.ten_hoc_phan} ({hoc_phan.ma_hoc_phan})"))
                    else:
                        updated_hp_count += 1
                        self.stdout.write(self.style.SUCCESS(f"  Updated HocPhan: {hoc_phan.ten_hoc_phan} ({hoc_phan.ma_hoc_phan})"))

                    # --- 2. Handle ChuongTrinhDaoTao (Training Program) ---
                    # The CSV only provides MaKhoi, so we need to create CTDT if it doesn't exist
                    # with placeholder/default values for other required fields.
                    # You might need to manually update these CTDTs later or provide a more comprehensive CTDT import.
                    
                    # Attempt to find NganhDaoTao based on MaBH or ChuyenNganh if available and meaningful
                    # For now, we'll create a placeholder CTDT if not found.
                    
                    # Example: If MaKhoi is 'DA25ANH', we might assume ten_nganh_ctdt is 'Chương trình DA25ANH'
                    # and trinh_do_dao_tao is 'DH' (Đại học) by default.
                    
                    ctdt, created_ctdt = ChuongTrinhDaoTao.objects.get_or_create(
                        ma_nganh_ctdt=ma_khoi_ctdt,
                        defaults={
                            'ten_nganh_ctdt': f"Chương trình {ma_khoi_ctdt}", # Placeholder name
                            'trinh_do_dao_tao': 'DH', # Default
                            'hinh_thuc_dao_tao': 'CQ', # Default
                            'so_tin_chi_yeu_cau': 0, # Default
                            'ghi_chu_ctdt': ghi_chu_1, # Use GhiChu1 for CTDT notes
                            # Other fields will be null/default
                        }
                    )
                    if created_ctdt:
                        self.stdout.write(self.style.WARNING(f"  Created placeholder ChuongTrinhDaoTao: {ctdt.ten_nganh_ctdt} ({ctdt.ma_nganh_ctdt}). Please update its details manually if needed."))

                    # --- 3. Handle ChiTietHocPhanTrongCTDT (Course Module in Training Program Details) ---
                    try:
                        nhhk_int = int(nhhk)
                        is_mhbb_bool = bool(int(is_mhbb)) if is_mhbb else True # 1 for True, 0 for False, default to True if empty
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f"Skipping row due to invalid number format for ChiTietHocPhanTrongCTDT fields: {row} - Error: {e}"))
                        skipped_rows_count += 1
                        continue

                    chi_tiet_hp_ctdt, created_ctdt_hp = ChiTietHocPhanTrongCTDT.objects.update_or_create(
                        chuong_trinh_dao_tao=ctdt,
                        hoc_phan=hoc_phan,
                        defaults={
                            'la_bat_buoc': is_mhbb_bool,
                            'hoc_ky_du_kien': nhhk_int,
                            'so_gio_ly_thuyet_apdung': lt_tiet_int,
                            'so_gio_thuc_hanh_apdung': th_tiet_int,
                            'ghi_chu_trong_ctdt': ghi_chu_1, # Use GhiChu1 for CTHP notes
                            # tin_chi_ly_thuyet_apdung and tin_chi_thuc_hanh_apdung are not directly in CSV,
                            # but can be derived or left to default to HocPhan's values via property.
                        }
                    )
                    if created_ctdt_hp:
                        imported_ctdt_hp_count += 1
                        self.stdout.write(self.style.SUCCESS(f"  Linked {hoc_phan.ma_hoc_phan} to {ctdt.ma_nganh_ctdt} (Created)"))
                    else:
                        updated_ctdt_hp_count += 1
                        self.stdout.write(self.style.SUCCESS(f"  Linked {hoc_phan.ma_hoc_phan} to {ctdt.ma_nganh_ctdt} (Updated)"))

                self.stdout.write(self.style.SUCCESS(f"\nImport complete!"))
                self.stdout.write(self.style.SUCCESS(f"HocPhan imported: {imported_hp_count}, updated: {updated_hp_count}"))
                self.stdout.write(self.style.SUCCESS(f"ChiTietHocPhanTrongCTDT imported: {imported_ctdt_hp_count}, updated: {updated_ctdt_hp_count}"))
                self.stdout.write(self.style.WARNING(f"Total rows skipped due to errors: {skipped_rows_count}"))

        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist.')
        except Exception as e:
            raise CommandError(f'An error occurred during import: {e}')
