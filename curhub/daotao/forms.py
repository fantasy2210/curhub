from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset, Submit, HTML
from .models import (
    NganhDaoTao, ChuongTrinhDaoTao, HocPhan, ChiTietHocPhanTrongCTDT,
    DonViDaoTao, MucTieuDaoTao, ChuanDauRa
)

class NganhDaoTaoForm(forms.ModelForm):
    class Meta:
        model = NganhDaoTao
        fields = '__all__'

class ChuongTrinhDaoTaoModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(
                        'Thông tin Định danh',
                        Row(
                            Column('ma_nganh_ctdt', css_class='form-group col-md-6 mb-0'),
                            Column('ten_nganh_ctdt', css_class='form-group col-md-6 mb-0'),
                        ),
                        'ten_tieng_anh',
                        css_class='card-body'
                    ),
                    Fieldset(
                        'Thông tin Mô tả',
                        'mo_ta_chung',
                        'doi_tuong_tuyen_sinh',
                        'dieu_kien_tot_nghiep',
                        'chuong_trinh_tham_khao',
                        css_class='card-body'
                    ),
                    css_class='col-lg-8'
                ),
                Column(
                    Fieldset(
                        'Thuộc tính & Phân loại',
                        'don_vi_quan_ly',
                        'nganh_hoc_chung',
                        'trinh_do_dao_tao',
                        'hinh_thuc_dao_tao',
                        'van_bang_tot_nghiep',
                        'so_tin_chi_yeu_cau',
                        'thoi_gian_dao_tao',
                        css_class='card-body'
                    ),
                    Fieldset(
                        'Thông tin Ban hành',
                        'so_quyet_dinh_ban_hanh',
                        'ngay_ban_hanh_qd',
                        'ghi_chu_ctdt',
                        css_class='card-body'
                    ),
                    Submit('submit', 'Lưu Chương Trình', css_class='btn btn-primary w-100'),
                    HTML('<a href="{% url \'daotao:danh_sach_ctdt\' %}" class="btn btn-secondary w-100 mt-2">Hủy</a>'),
                    css_class='col-lg-4'
                )
            )
        )

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
            # Textarea fields for Summernote
            'mo_ta_chung': forms.Textarea(attrs={'class': 'summernote'}),
            'doi_tuong_tuyen_sinh': forms.Textarea(attrs={'class': 'summernote'}),
            'dieu_kien_tot_nghiep': forms.Textarea(attrs={'class': 'summernote'}),
            'chuong_trinh_tham_khao': forms.Textarea(attrs={'class': 'summernote'}),
            'ghi_chu_ctdt': forms.Textarea(attrs={'rows': 3}),

            # Select fields for Select2
            'nganh_hoc_chung': forms.Select(attrs={'class': 'select2'}),
            'trinh_do_dao_tao': forms.Select(attrs={'class': 'select2'}),
            'hinh_thuc_dao_tao': forms.Select(attrs={'class': 'select2'}),
            'van_bang_tot_nghiep': forms.Select(attrs={'class': 'select2'}),
            'don_vi_quan_ly': forms.Select(attrs={'class': 'select2'}),
            
            # Date picker
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
