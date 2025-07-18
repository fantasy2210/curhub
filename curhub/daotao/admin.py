from django.contrib import admin
from .models import (
    DonViDaoTao, NganhDaoTao, DanhMucKienThuc, HocPhan, 
    ChuongTrinhDaoTao, MucTieuDaoTao, ChuanDauRa, ChiTietHocPhanTrongCTDT,
    DeCuongHocPhan, ChuanDauRaHocPhan, MaTranCDR_CTHP,
    LichSuThayDoiCTDT
)

# Hiển thị lịch sử thay đổi ngay trong trang CTĐT
class LichSuThayDoiCTDTInline(admin.TabularInline):
    model = LichSuThayDoiCTDT
    extra = 0
    fields = ('thoi_gian', 'nguoi_thuc_hien', 'hanh_dong', 'chi_tiet_thay_doi')
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

# Cấu hình cho model ChuongTrinhDaoTao
@admin.register(ChuongTrinhDaoTao)
class ChuongTrinhDaoTaoAdmin(admin.ModelAdmin):
    list_display = ('ten_nganh_ctdt', 'ma_nganh_ctdt', 'trinh_do_dao_tao', 'version', 'trang_thai', 'don_vi_quan_ly')
    list_filter = ('trinh_do_dao_tao', 'hinh_thuc_dao_tao', 'trang_thai', 'don_vi_quan_ly')
    search_fields = ('ten_nganh_ctdt', 'ma_nganh_ctdt')
    readonly_fields = ('ngay_tao', 'ngay_cap_nhat')
    inlines = [LichSuThayDoiCTDTInline] # Hiển thị lịch sử ở đây

# Đăng ký các model khác (giữ nguyên nếu bạn đã có)
admin.site.register(DonViDaoTao)
admin.site.register(NganhDaoTao)
admin.site.register(DanhMucKienThuc)
admin.site.register(HocPhan)
admin.site.register(MucTieuDaoTao)
admin.site.register(ChuanDauRa)
admin.site.register(ChiTietHocPhanTrongCTDT)
admin.site.register(DeCuongHocPhan)
admin.site.register(ChuanDauRaHocPhan)
admin.site.register(MaTranCDR_CTHP)
admin.site.register(LichSuThayDoiCTDT)