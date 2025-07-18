import csv
from django.core.management.base import BaseCommand
from daotao.models import HocPhan, DonViDaoTao
import os

class Command(BaseCommand):
    help = 'Import học phần từ file CSV có tên danh_sach_hoc_phan.csv'

    def handle(self, *args, **options):
        # Đường dẫn đến file CSV, giả sử nó nằm trong thư mục 'curhub' con của thư mục gốc dự án
        file_path = os.path.join(os.getcwd(), 'curhub', 'danh_sach_hoc_phan.csv')
        self.stdout.write(self.style.SUCCESS(f"Bắt đầu import học phần từ file {file_path}..."))

        # Bảng ánh xạ mã đơn vị từ file CSV sang mã trong CSDL.
        # BẠN CÓ THỂ BỔ SUNG THÊM VÀO ĐÂY NẾU SCRIPT VẪN BÁO KHÔNG TÌM THẤY
        don_vi_mapping = {
            'HHUD': 'BM_HHUD',
            'BMCKDL': 'BM_CK_DL',
            'BMVHH-XHH': 'BM_VHH',
            'QLNN,QTVP&': 'K_QLNN_QTVP_DL',
            'BMCNTY': 'BM_CNTY',
            'SP': 'K_SP',
            'BMTS': 'BM_THUYSAN',
            'KT-CN': 'K_KTCN',
            'BMKTO': 'BM_KETOAN',
            'BMXD': 'BM_XD',
            'BML': 'BM_LUAT',
            'KNNVHNTKMNB_TRUONG.N': 'K_NNVHNTKNB',
            'TRUONG.NNVHNTKNB&NV': 'T_NNVHKNB',
            'BMDL': 'BM_DULICH',
            'BMKT': 'BM_KT',
            'BMĐD': 'BM_DD',
            'TTCNSTH': 'TT_CNSTH',
            'BMTL': 'BM_TAMLY_CTXH', # Giả định BMTL là Bộ môn Tâm Lý
            'BMSPTH': 'BM_SPTH',
            'BMXNYK': 'BM_XNYK',
            'YD': 'K_YD',
            'BMQT': 'K_QT',
            'KHCB': 'K_KHCB',
            'KRHM': 'K_RHM',
            'BMYTCC': 'BM_YTCC',
            'P.ĐT': 'P_DT',
            'BMSPNV': 'BM_SPNV',
            'BMTA': 'BM_TA',
            'AV': 'BM_TA', # Giả định AV là Anh Văn -> Bộ môn Tiếng Anh
            'BMTTPTNT': 'BM_TT_PTNT',
            'BMSPNH': 'BM_SPNH',
            'BMUDCDLHVL': 'BM_UDCDLHVL',
            'BMNT': 'BM_NT',
            'KLLCT': 'K_LLCT',
            'BMDTVT': 'BM_DT_VT',
            'DB': 'K_DBDH', # Giả định DB là Khoa Dự bị Đại học
            'BMQTVPTV': 'BM_QTVP_TV',
            'VKHCNMT': 'V_KHCNMT',
            'BMNC': 'BM_NUCONG', # Giả định BMNC là Bộ môn Nữ công
            'TRUONG.YD_TVU': 'T_YD',
            'TT.GDQP&AN': 'TT_GDQPAN',
            'KQT_TRUONG.KT,L': 'K_QT',
            'KT-L': 'K_KTL',
            'TTCNSH&MT': 'TT_CNSH', # Giả định
            'BMDDL': 'BM_DDL',
            'BMSPMN': 'BM_SPMN',
            'BMTUD': 'BM_TUD',
            'BMD': 'BM_D',
            'BM_UDCDLHVL': 'BM_UDCDLHVL', # Corrected from BMUDCDLHVL
            'BMCNTT': 'BM_CNTT',
            'K.GDTC_TVU': 'K_GDTC_TVU',
            'BMTCNH': 'BM_TCNH',
            'TT_ĐTLOGISTICS&TMĐT': 'TT_DTL_TMDT',
            'BMNNKh': 'BM_NNKHMER',
            'BMHOA': 'BM_HOASINH', # Assuming BMHOA maps to BM_HOASINH
        }
        
        don_vi_cache = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Đọc file CSV bằng DictReader
                reader = csv.DictReader(file)
                total_rows = 0
                created_count = 0
                updated_count = 0
                error_count = 0

                for row in reader:
                    total_rows += 1
                    ma_mh = row.get('MaMH', '').strip()
                    if not ma_mh:
                        self.stdout.write(self.style.WARNING(f"Dòng {total_rows+1}: Thiếu 'MaMH'. Bỏ qua."))
                        error_count += 1
                        continue

                    # --- Tìm đơn vị quản lý ---
                    don_vi_quan_ly = None
                    ma_dv_csv = row.get('MaDV', '').strip()
                    if ma_dv_csv:
                        ma_dv_chuan = don_vi_mapping.get(ma_dv_csv, ma_dv_csv)
                        
                        if ma_dv_chuan in don_vi_cache:
                            don_vi_quan_ly = don_vi_cache[ma_dv_chuan]
                        else:
                            try:
                                don_vi_quan_ly = DonViDaoTao.objects.get(ma_don_vi__iexact=ma_dv_chuan)
                                don_vi_cache[ma_dv_chuan] = don_vi_quan_ly
                            except DonViDaoTao.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f"HP '{ma_mh}': Không tìm thấy ĐV có mã '{ma_dv_chuan}' (từ mã gốc '{ma_dv_csv}')."))

                    # --- Xử lý các giá trị số ---
                    try:
                        tong_so_tin_chi = int(float(row.get('SoTinChi') or 0))
                        # Giả định cột LT là tín chỉ lý thuyết
                        tin_chi_lt = int(float(row.get('LT') or 0))
                        tin_chi_th = tong_so_tin_chi - tin_chi_lt if tong_so_tin_chi >= tin_chi_lt else 0
                        so_tiet_tong_cong = int(float(row.get('SoTietMH') or 0)) if row.get('SoTietMH') else None
                        so_tin_chi_ects = float(row.get('SoTinChiEU')) if row.get('SoTinChiEU') else None
                    except (ValueError, TypeError):
                        self.stdout.write(self.style.ERROR(f"HP '{ma_mh}': Lỗi dữ liệu số. Bỏ qua."))
                        error_count += 1
                        continue

                    # --- Xử lý các giá trị boolean ---
                    is_tu_chon = True if row.get('IsMHTN') == '1' else False
                    khong_tinh_dtb = True if row.get('KhgTinhDTB') == '1' else False

                    # Tạo dictionary chứa các giá trị để tạo hoặc cập nhật
                    defaults_data = {
                        'ten_hoc_phan': row.get('TenMH', ''),
                        'ten_tieng_anh': row.get('TenMHEg') or None,
                        'tong_so_tin_chi_goc': tong_so_tin_chi,
                        'tin_chi_ly_thuyet_goc': tin_chi_lt,
                        'tin_chi_thuc_hanh_goc': tin_chi_th,
                        'so_tiet_tong_cong': so_tiet_tong_cong,
                        'so_tin_chi_ects': so_tin_chi_ects,
                        'don_vi_quan_ly_goc': don_vi_quan_ly,
                        'la_hoc_phan_tu_chon': is_tu_chon,
                        'khong_tinh_diem_tb': khong_tinh_dtb,
                    }

                    # Sử dụng update_or_create để không bị lỗi nếu chạy lại lệnh
                    obj, created = HocPhan.objects.update_or_create(
                        ma_hoc_phan=ma_mh,
                        defaults=defaults_data
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'\nHoàn thành!'))
                self.stdout.write(f'Tổng số dòng đã xử lý: {total_rows}')
                self.stdout.write(self.style.SUCCESS(f'Đã tạo mới: {created_count} học phần'))
                self.stdout.write(self.style.NOTICE(f'Đã cập nhật: {updated_count} học phần'))
                if error_count > 0:
                    self.stdout.write(self.style.ERROR(f'Có {error_count} lỗi trong quá trình xử lý. Vui lòng kiểm tra lại dữ liệu.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Không tìm thấy file {file_path}. Vui lòng đặt file này ở thư mục gốc của dự án."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Đã có lỗi nghiêm trọng xảy ra: {e}"))
