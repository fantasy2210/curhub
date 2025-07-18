from django.urls import path
from django.views.generic.base import RedirectView # Import RedirectView
from . import views

app_name = 'daotao' # Đặt tên ứng dụng để sử dụng trong template (ví dụ: daotao:them_nganh)

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='daotao:danh_sach_ctdt', permanent=False)), # Redirect base daotao/ to danh_sach_ctdt/
    # URL cho Ngành Đào tạo
    path('them-nganh/', views.them_nganh_dao_tao, name='them_nganh_dao_tao'),

    # URL cho Chương trình Đào tạo
    path('them-ctdt/', views.them_chuong_trinh_dao_tao, name='them_ctdt'),
    path('danh-sach-ctdt/', views.danh_sach_ctdt, name='danh_sach_ctdt'),
    path('chi-tiet-ctdt/<int:pk_ctdt>/', views.chi_tiet_ctdt, name='chi_tiet_ctdt'),
    path('sua-ctdt/<int:pk_ctdt>/', views.sua_ctdt, name='sua_ctdt'),
    path('xoa-ctdt/<int:pk_ctdt>/', views.xoa_ctdt, name='xoa_ctdt'),
    path('ctdt/<int:pk_ctdt>/gui-duyet/', views.gui_duyet_ctdt, name='gui_duyet_ctdt'),
    path('ctdt/<int:pk_ctdt>/xu-ly-duyet/<str:action>/', views.xu_ly_duyet_ctdt, name='xu_ly_duyet_ctdt'),
    path('ctdt/<int:pk_ctdt>/tao-phien-ban-moi/', views.tao_phien_ban_moi_ctdt, name='tao_phien_ban_moi_ctdt'),
    path('ctdt/<int:pk_ctdt>/luu-tru/', views.luu_tru_ctdt, name='luu_tru_ctdt'),
    path('ctdt/<int:pk_ctdt>/upload-hoc-phan/', views.upload_hoc_phan_ctdt, name='upload_hoc_phan_ctdt'),
    path('download-hoc-phan-template/', views.download_hoc_phan_ctdt_template, name='download_hoc_phan_ctdt_template'),

    # URL cho Học phần trong CTĐT (ChiTietHocPhanTrongCTDT)
    path('them-hoc-phan-vao-ctdt/', views.them_hoc_phan_vao_ctdt, name='them_hoc_phan_vao_ctdt'),
    path('ctdt/<int:pk_ctdt>/danh-sach-hoc-phan/', views.danh_sach_hoc_phan_theo_ctdt, name='danh_sach_hoc_phan_theo_ctdt'),
    path('chi-tiet-hp-ctdt/<int:pk_chi_tiet_hp>/', views.chi_tiet_hoc_phan_trong_ctdt, name='chi_tiet_hoc_phan_trong_ctdt'),
    path('sua-chi-tiet-hp-ctdt/<int:pk_chi_tiet_hp>/', views.sua_chi_tiet_hp_trong_ctdt, name='sua_chi_tiet_hp_trong_ctdt'),
    path('xoa-chi-tiet-hp-ctdt/<int:pk_chi_tiet_hp>/', views.xoa_chi_tiet_hp_trong_ctdt, name='xoa_chi_tiet_hp_trong_ctdt'),
    path('ctdt/<int:pk_ctdt>/them-hoc-phan-hang-loat/', views.them_hoc_phan_hang_loat, name='them_hoc_phan_hang_loat'), # Ensure this line is present and correct

    # URL cho Học phần (thư viện chung)
    path('danh-sach-hoc-phan/', views.danh_sach_hoc_phan, name='danh_sach_hoc_phan'),
    path('sua-hoc-phan/<int:pk_hoc_phan>/', views.sua_hoc_phan, name='sua_hoc_phan'),
    path('xoa-hoc-phan/<int:pk_hoc_phan>/', views.xoa_hoc_phan, name='xoa_hoc_phan'),

    # URL cho Đơn vị Đào tạo
    path('danh-sach-don-vi/', views.danh_sach_don_vi, name='danh_sach_don_vi'),
    path('them-don-vi/', views.them_don_vi, name='them_don_vi'),
    path('sua-don-vi/<int:pk_don_vi>/', views.sua_don_vi, name='sua_don_vi'),
    path('xoa-don-vi/<int:pk_don_vi>/', views.xoa_don_vi, name='xoa_don_vi'),

    # URLs cho Chuẩn Đầu Ra (PLO)
    path('ctdt/<int:pk_ctdt>/them-cdr/', views.them_chuan_dau_ra, name='them_chuan_dau_ra'),
    path('sua-cdr/<int:pk_cdr>/', views.sua_chuan_dau_ra, name='sua_chuan_dau_ra'),
    path('xoa-cdr/<int:pk_cdr>/', views.xoa_chuan_dau_ra, name='xoa_chuan_dau_ra'),

    # Placeholder URLs cho Mục tiêu Đào tạo (PO)
    path('ctdt/<int:pk_ctdt>/them-mt/', views.them_muc_tieu_dao_tao, name='them_muc_tieu_dao_tao'),
    path('sua-mt/<int:pk_po>/', views.sua_muc_tieu_dao_tao, name='sua_muc_tieu_dao_tao'),
    path('xoa-mt/<int:pk_po>/', views.xoa_muc_tieu_dao_tao, name='xoa_muc_tieu_dao_tao'),
]
