from django import forms
from .models import ChuongTrinhDaoTao # và các model khác nếu cần

class ChuongTrinhDaoTaoModelForm(forms.ModelForm):
    class Meta:
        model = ChuongTrinhDaoTao
        fields = [
            'ma_nganh_ctdt', 'ten_nganh_ctdt', 'ten_tieng_anh', 'nganh_hoc_chung',
            'trinh_do_dao_tao', 'hinh_thuc_dao_tao', 'so_tin_chi_yeu_cau', 
            'thoi_gian_dao_tao', 'doi_tuong_tuyen_sinh', 'dieu_kien_tot_nghiep',
            'van_bang_tot_nghiep', 'chuong_trinh_tham_khao', 'don_vi_quan_ly', 'mo_ta_chung'
        ]
        widgets = {
            'ma_nganh_ctdt': forms.TextInput(attrs={'placeholder': 'Ví dụ: 7480201CDSP'}),
            'ten_nganh_ctdt': forms.TextInput(attrs={'placeholder': 'Nhập tên chương trình đào tạo bằng Tiếng Việt'}),
            'ten_tieng_anh': forms.TextInput(attrs={'placeholder': 'Nhập tên chương trình đào tạo bằng Tiếng Anh'}),
            'so_tin_chi_yeu_cau': forms.NumberInput(attrs={'placeholder': 'Ví dụ: 120'}),
            'thoi_gian_dao_tao': forms.TextInput(attrs={'placeholder': 'Ví dụ: 3.5 năm, 2 năm...'}),
            'doi_tuong_tuyen_sinh': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Nhập đối tượng tuyển sinh'}),
            'dieu_kien_tot_nghiep': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Nhập các điều kiện để tốt nghiệp'}),
            'chuong_trinh_tham_khao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Liệt kê các chương trình trong và ngoài nước đã tham khảo'}),
            'mo_ta_chung': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Nhập mô tả tổng quan về chương trình đào tạo'}),
            
            # Các trường select sẽ được áp class 'form-select' tự động qua template tag
            'nganh_hoc_chung': forms.Select(),
            'trinh_do_dao_tao': forms.Select(),
            'hinh_thuc_dao_tao': forms.Select(),
            'van_bang_tot_nghiep': forms.Select(),
            'don_vi_quan_ly': forms.Select(),
        }