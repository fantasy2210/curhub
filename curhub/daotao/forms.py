from django import forms
from django.forms import inlineformset_factory
from .models import NganhDaoTao, ChuongTrinhDaoTao, HocPhan, ChiTietHocPhanTrongCTDT, DanhMucKienThuc, DonViDaoTao, MucTieuDaoTao, ChuanDauRa

# Mẫu biểu mẫu cho Ngành Đào tạo
class NganhDaoTaoForm(forms.ModelForm):
    class Meta:
        model = NganhDaoTao
        fields = ['ma_nganh', 'ten_nganh', 'mo_ta']
        widgets = {
            'mo_ta': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'ma_nganh': forms.TextInput(attrs={'placeholder': 'Nhập mã ngành'}),
            'ten_nganh': forms.TextInput(attrs={'placeholder': 'Nhập tên ngành'}),
        }
        labels = {
            'ma_nganh': 'Mã Ngành',
            'ten_nganh': 'Tên Ngành',
            'mo_ta': 'Mô tả',
        }
        help_texts = {
            'ma_nganh': 'Nhập mã ngành duy nhất.',
            'ten_nganh': 'Nhập tên tên ngành đào tạo.',
            'mo_ta': 'Nhập mô tả ngắn về ngành đào tạo.',
        }
        error_messages = {
            'ma_nganh': {
                'required': 'Mã ngành là bắt buộc.',
                'unique': 'Mã ngành này đã tồn tại.',   
            },
            'ten_nganh': {
                'required': 'Tên ngành là bắt buộc.',
            }}
        

# Mẫu biểu mẫu cho Chương trình Đào tạo
class ChuongTrinhDaoTaoModelForm(forms.ModelForm):
    class Meta:
        model = ChuongTrinhDaoTao
        fields = [
            'ma_nganh_ctdt', 
            'ten_nganh_ctdt',
            'ten_tieng_anh',         # Trường mới
            'nganh_hoc_chung',       # Trường mới (ForeignKey đến NganhDaoTao)
            'trinh_do_dao_tao', 
            'hinh_thuc_dao_tao', 
            'so_tin_chi_yeu_cau',    # Trường mới
            'thoi_gian_dao_tao', 
            'doi_tuong_tuyen_sinh',  # Trường mới
            'dieu_kien_tot_nghiep',  # Trường mới
            'van_bang_tot_nghiep',   # Trường mới
            'chuong_trinh_tham_khao',# Trường mới
            'don_vi_quan_ly', 
            'mo_ta_chung',
        ]

        labels = {
            'ma_nganh_ctdt': 'Mã chương trình/ngành đào tạo',
            'ten_nganh_ctdt': 'Tên chương trình đào tạo (Tiếng Việt)',
            'ten_tieng_anh': 'Tên chương trình đào tạo (Tiếng Anh)',
            'nganh_hoc_chung': 'Thuộc Ngành học (chung)',
            'trinh_do_dao_tao': 'Trình độ đào tạo',
            'hinh_thuc_dao_tao': 'Hình thức đào tạo',
            'so_tin_chi_yeu_cau': 'Tổng số tín chỉ yêu cầu',
            'thoi_gian_dao_tao': 'Thời gian đào tạo (ví dụ: 3.5 năm)',
            'doi_tuong_tuyen_sinh': 'Đối tượng tuyển sinh',
            'dieu_kien_tot_nghiep': 'Điều kiện tốt nghiệp',
            'van_bang_tot_nghiep': 'Văn bằng tốt nghiệp',
            'chuong_trinh_tham_khao': 'Chương trình đào tạo tham khảo',
            'don_vi_quan_ly': 'Đơn vị quản lý',
            'mo_ta_chung': 'Mô tả chung về CTĐT',
        }

        widgets = {
            'mo_ta_chung': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Nhập mô tả chi tiết...'}),
            'doi_tuong_tuyen_sinh': forms.Textarea(attrs={'rows': 3}),
            'dieu_kien_tot_nghiep': forms.Textarea(attrs={'rows': 3}),
            'chuong_trinh_tham_khao': forms.Textarea(attrs={'rows': 3}),
            'ma_nganh_ctdt': forms.TextInput(attrs={'placeholder': 'Ví dụ: 7480201CDSP'}),
            'thoi_gian_dao_tao': forms.TextInput(attrs={'placeholder': 'Ví dụ: 3.5 năm, 2 năm...'}),
        }

# Form cho Mục tiêu Đào tạo (PO)
class MucTieuDaoTaoForm(forms.ModelForm):
    class Meta:
        model = MucTieuDaoTao
        fields = ['ma_muc_tieu', 'noi_dung']
        labels = {
            'ma_muc_tieu': 'Mã Mục tiêu',
            'noi_dung': 'Nội dung Mục tiêu',
        }
        widgets = {
            'noi_dung': forms.Textarea(attrs={'rows': 2}),
        }

# Form cho Chuẩn Đầu Ra (PLO)
class ChuanDauRaForm(forms.ModelForm):
    class Meta:
        model = ChuanDauRa
        fields = ['ma_cdr', 'noi_dung', 'dap_ung_muc_tieu']
        labels = {
            'ma_cdr': 'Mã Chuẩn đầu ra',
            'noi_dung': 'Nội dung Chuẩn đầu ra',
            'dap_ung_muc_tieu': 'Đáp ứng Mục tiêu đào tạo (PO)',
        }
        widgets = {
            'noi_dung': forms.Textarea(attrs={'rows': 2}),
        }

# Formset cho Mục tiêu Đào tạo
MucTieuDaoTaoFormSet = inlineformset_factory(
    ChuongTrinhDaoTao, 
    MucTieuDaoTao, 
    form=MucTieuDaoTaoForm, 
    extra=1, 
    can_delete=True
)

# Formset cho Chuẩn Đầu Ra
ChuanDauRaFormSet = inlineformset_factory(
    ChuongTrinhDaoTao, 
    ChuanDauRa, 
    form=ChuanDauRaForm, 
    extra=1, 
    can_delete=True
)

# Form này có thể dùng để quản lý thư viện HocPhan chung (nếu cần)
class HocPhanLibModelForm(forms.ModelForm): # Đổi tên để tránh nhầm lẫn
    class Meta:
        model = HocPhan # Dựa trên model HocPhan chung
        fields = [
            'ma_hoc_phan',
            'ten_hoc_phan',
            'ten_tieng_anh', # Added
            'tin_chi_ly_thuyet_goc',
            'tin_chi_thuc_hanh_goc',
            'tong_so_tin_chi_goc', # Added
            'so_gio_ly_thuyet_goc',
            'so_gio_thuc_hanh_goc',
            'so_gio_tu_hoc_goc',
            'mo_ta_hoc_phan',
        ]
        labels = {
            'ma_hoc_phan': 'Mã học phần (chung)',
            'ten_hoc_phan': 'Tên học phần (chung)',
            'ten_tieng_anh': 'Tên học phần (Tiếng Anh)', # Added
            'tin_chi_ly_thuyet_goc': 'Số TC LT gốc',
            'tin_chi_thuc_hanh_goc': 'Số TC TH gốc',
            'tong_so_tin_chi_goc': 'Tổng số TC gốc', # Added
            'so_gio_ly_thuyet_goc': 'Số giờ LT gốc',
            'so_gio_thuc_hanh_goc': 'Số giờ TH gốc',
            'so_gio_tu_hoc_goc': 'Số giờ tự học gốc',
            'mo_ta_hoc_phan': 'Mô tả tóm tắt',
        }
        widgets = {
            'mo_ta_hoc_phan': forms.Textarea(attrs={'rows': 3}),
        }

# Form mới để quản lý chi tiết học phần TRONG một CTĐT
class ChiTietHocPhanTrongCTDTModelForm(forms.ModelForm):
    # Ghi đè để các trường này không bắt buộc, phục vụ cho chức năng thêm hàng loạt
    # nơi người dùng có thể không cung cấp các giá trị này ngay lập tức.
    danh_muc_kien_thuc = forms.ModelChoiceField(queryset=DanhMucKienThuc.objects.all(), required=False, label='Phân loại trong CTĐT này')
    la_bat_buoc = forms.BooleanField(required=False, initial=True, label='Bắt buộc trong CTĐT này?')
    hoc_ky_du_kien = forms.IntegerField(required=False, label='Học kỳ dự kiến')

    class Meta:
        model = ChiTietHocPhanTrongCTDT
        fields = [
            'chuong_trinh_dao_tao', # Chọn CTĐT
            'hoc_phan',             # Chọn Học phần từ thư viện
            'danh_muc_kien_thuc',   # Chọn Danh mục kiến thức cho HP này trong CTĐT này
            'la_bat_buoc',
            'hoc_ky_du_kien',
            'tin_chi_ly_thuyet_apdung',
            'tin_chi_thuc_hanh_apdung',
            'so_gio_ly_thuyet_apdung',
            'so_gio_thuc_hanh_apdung',
            'so_gio_tu_hoc_apdung',
            'so_tiet_ly_thuyet_online', # <<-- THÊM TRƯỜNG MỚI
            'ghi_chu_trong_ctdt',
        ]
        labels = {
            'chuong_trinh_dao_tao': 'Thuộc Chương trình Đào tạo',
            'hoc_phan': 'Chọn Học phần (từ thư viện)',
            # 'danh_muc_kien_thuc': 'Phân loại trong CTĐT này', # Đã định nghĩa ở trên
            # 'la_bat_buoc': 'Bắt buộc trong CTĐT này?', # Đã định nghĩa ở trên
            # 'hoc_ky_du_kien': 'Học kỳ dự kiến', # Đã định nghĩa ở trên
            'tin_chi_ly_thuyet_apdung': 'Số TC LT áp dụng',
            'tin_chi_thuc_hanh_apdung': 'Số TC TH áp dụng',
             'so_tiet_ly_thuyet_online': 'Số tiết Lý thuyết Online', # <<-- THÊM LABEL MỚI
            'ghi_chu_trong_ctdt': 'Ghi chú riêng cho CTĐT (nếu có thông tin khác về online, ghi ở đây)',
        }

class ThemHocPhanHangLoatForm(forms.Form):
    # This field will be populated dynamically in the view
    hoc_phans = forms.ModelMultipleChoiceField(
        queryset=HocPhan.objects.all().order_by('ma_hoc_phan'),
        widget=forms.CheckboxSelectMultiple,
        label="Chọn các Học phần",
        help_text="Chọn một hoặc nhiều học phần để thêm vào chương trình đào tạo này."
    )

    def __init__(self, *args, **kwargs):
        self.chuong_trinh_dao_tao = kwargs.pop('chuong_trinh_dao_tao', None)
        super().__init__(*args, **kwargs)
        if self.chuong_trinh_dao_tao:
            # Filter out hoc_phans already associated with this CTDT
            existing_hoc_phans_ids = ChiTietHocPhanTrongCTDT.objects.filter(
                chuong_trinh_dao_tao=self.chuong_trinh_dao_tao
            ).values_list('hoc_phan__id', flat=True)
            self.fields['hoc_phans'].queryset = HocPhan.objects.exclude(
                id__in=existing_hoc_phans_ids
            ).order_by('ma_hoc_phan')
            
            if not self.fields['hoc_phans'].queryset.exists():
                self.fields['hoc_phans'].help_text = "Tất cả học phần đã được thêm vào chương trình đào tạo này."
                self.fields['hoc_phans'].widget.attrs['disabled'] = 'disabled'


class DonViDaoTaoForm(forms.ModelForm):
    class Meta:
        model = DonViDaoTao
        fields = ['ma_don_vi', 'ten_don_vi', 'don_vi_cha', 'mo_ta']
        labels = {
            'ma_don_vi': 'Mã đơn vị',
            'ten_don_vi': 'Tên đơn vị đào tạo',
            'don_vi_cha': 'Đơn vị cha',
            'mo_ta': 'Mô tả đơn vị',
        }
        widgets = {
            'mo_ta': forms.Textarea(attrs={'rows': 3}),
        }

class UploadHocPhanCTDTForm(forms.Form):
    file = forms.FileField(label='Chọn tệp Excel/CSV', help_text='Tải lên danh sách học phần để thêm vào chương trình đào tạo.')
