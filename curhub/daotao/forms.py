from django import forms
from django.forms import inlineformset_factory
from .models import (
    NganhDaoTao, ChuongTrinhDaoTao, HocPhan, ChiTietHocPhanTrongCTDT,
    DonViDaoTao, MucTieuDaoTao, ChuanDauRa
)

class NganhDaoTaoForm(forms.ModelForm):
    class Meta:
        model = NganhDaoTao
        fields = '__all__'

class ChuongTrinhDaoTaoModelForm(forms.ModelForm):
    class Meta:
        model = ChuongTrinhDaoTao
        fields = [
            'ma_nganh_ctdt', 'ten_nganh_ctdt', 'ten_tieng_anh', 'nganh_hoc_chung',
            'trinh_do_dao_tao', 'hinh_thuc_dao_tao', 'so_tin_chi_yeu_cau',
            'thoi_gian_dao_tao', 'doi_tuong_tuyen_sinh', 'dieu_kien_tot_nghiep',
            'van_bang_tot_nghiep', 'chuong_trinh_tham_khao', 'don_vi_quan_ly',
            'mo_ta_chung', 'so_quyet_dinh_ban_hanh', 'ngay_ban_hanh_qd', 'ghi_chu_ctdt'
        ]
        widgets = {
            'ngay_ban_hanh_qd': forms.DateInput(attrs={'type': 'date'}),
        }

class HocPhanLibModelForm(forms.ModelForm):
    class Meta:
        model = HocPhan
        fields = '__all__'

class ChiTietHocPhanTrongCTDTModelForm(forms.ModelForm):
    class Meta:
        model = ChiTietHocPhanTrongCTDT
        exclude = ('chuong_trinh_dao_tao', 'hoc_phan')

class DonViDaoTaoForm(forms.ModelForm):
    class Meta:
        model = DonViDaoTao
        fields = '__all__'

class MucTieuDaoTaoForm(forms.ModelForm):
    class Meta:
        model = MucTieuDaoTao
        fields = '__all__'
        exclude = ('chuong_trinh_dao_tao',) # Exclude FK as it's set in view

MucTieuDaoTaoFormSet = inlineformset_factory(
    ChuongTrinhDaoTao,
    MucTieuDaoTao,
    form=MucTieuDaoTaoForm,
    extra=1,
    can_delete=True
)

class ChuanDauRaForm(forms.ModelForm):
    class Meta:
        model = ChuanDauRa
        fields = '__all__'
        exclude = ('chuong_trinh_dao_tao',) # Exclude FK as it's set in view

ChuanDauRaFormSet = inlineformset_factory(
    ChuongTrinhDaoTao,
    ChuanDauRa,
    form=ChuanDauRaForm,
    extra=1,
    can_delete=True
)

class UploadHocPhanCTDTForm(forms.Form):
    file = forms.FileField(label="Chọn tệp Excel (.xlsx) hoặc CSV (.csv)")
