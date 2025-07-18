from django.db import models
# from django.utils import timezone # Hiện tại chưa dùng trực tiếp ở đây

class DonViDaoTao(models.Model):
    ma_don_vi = models.CharField(max_length=20, unique=True, verbose_name="Mã đơn vị")
    ten_don_vi = models.CharField(max_length=255, verbose_name="Tên đơn vị đào tạo")
    don_vi_cha = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='don_vi_con',
        verbose_name="Đơn vị cha"
    )
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả đơn vị")
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    def __str__(self):
        if self.don_vi_cha:
            return f"{self.don_vi_cha.ten_don_vi} -> {self.ten_don_vi}"
        return self.ten_don_vi

    class Meta:
        verbose_name = "Đơn vị Đào tạo"
        verbose_name_plural = "Các Đơn vị Đào tạo"
        ordering = ['don_vi_cha__ten_don_vi', 'ten_don_vi']

# Model NganhDaoTao (bạn có thể giữ lại nếu nó phục vụ mục đích khác, 
# ví dụ như một danh mục ngành lớn hơn mà CTĐT có thể tham khảo)
class NganhDaoTao(models.Model):
    ma_nganh=models.CharField(max_length=20, unique=True,verbose_name="Mã Ngành (Danh mục)")
    ten_nganh=models.CharField(max_length=255,verbose_name="Tên Ngành (Danh mục)")
    mo_ta=models.TextField(blank=True,null=True,verbose_name="Mô tả")
    ngay_tao=models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_cap_nhat=models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    def __str__(self):
        return self.ten_nganh

    class Meta:
        verbose_name="Ngành đào tạo (Danh mục)"
        verbose_name_plural="Các ngành đào tạo (Danh mục)"

class DanhMucKienThuc(models.Model):
    ten_danh_muc = models.CharField(max_length=255, verbose_name="Tên danh mục kiến thức")
    ma_danh_muc = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Mã danh mục")
    danh_muc_cha = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='danh_muc_con',
        verbose_name="Danh mục cha"
    )
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả danh mục")
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    def __str__(self):
        # Sửa lại để tránh lỗi nếu danh_muc_cha là None và không có ten_don_vi
        if self.danh_muc_cha:
            try:
                # Giả sử __str__ của DanhMucKienThuc cha sẽ hiển thị tên của nó
                parent_name = str(self.danh_muc_cha) 
            except AttributeError: # Phòng trường hợp __str__ của cha phức tạp
                parent_name = self.danh_muc_cha.ten_danh_muc
            return f"{parent_name} -> {self.ten_danh_muc}"
        return self.ten_danh_muc

    class Meta:
        verbose_name = "Danh mục Kiến thức"
        verbose_name_plural = "Các Danh mục Kiến thức"
        ordering = ['danh_muc_cha__ten_danh_muc', 'ten_danh_muc']


# Trong daotao/models.py
# (Các import và các model khác đã có)

# Trong file: daotao/models.py
# (Các import và các model khác đã có)

# Trong file: daotao/models.py
# (Các import và các model khác đã có)

# Trong daotao/models.py
# (Các import và các model khác đã có)

# Trong file: daotao/models.py
# (Các import và các model khác đã có)

class HocPhan(models.Model): # Thư viện học phần chung
    ma_hoc_phan = models.CharField(max_length=20, unique=True, verbose_name="Mã học phần (MaMH)")
    ten_hoc_phan = models.CharField(max_length=255, verbose_name="Tên học phần (TenMH)")
    ten_tieng_anh = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên học phần (Tiếng Anh - TenMHEg)")
    
    tong_so_tin_chi_goc = models.PositiveIntegerField(default=0, verbose_name="Tổng số TC gốc (SoTinChi)")
    tin_chi_ly_thuyet_goc = models.PositiveIntegerField(default=0, verbose_name="Số TC Lý thuyết gốc")
    tin_chi_thuc_hanh_goc = models.PositiveIntegerField(default=0, verbose_name="Số TC Thực hành gốc")

    so_tiet_tong_cong = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tổng số tiết học (SoTietMH)")
    
    # BỔ SUNG CÁC TRƯỜNG GIỜ HỌC CÒN THIẾU
    so_gio_ly_thuyet_goc = models.PositiveIntegerField(default=0, verbose_name="Số giờ LT gốc")
    so_gio_thuc_hanh_goc = models.PositiveIntegerField(default=0, verbose_name="Số giờ TH gốc")
    so_gio_tu_hoc_goc = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name="Số giờ tự học/khác (gốc)")
    
    so_tin_chi_ects = models.FloatField(null=True, blank=True, verbose_name="Số tín chỉ ECTS (SoTinChiEU)")
    
    don_vi_quan_ly_goc = models.ForeignKey(
        DonViDaoTao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Đơn vị quản lý gốc (MaDV)"
    )

    la_hoc_phan_tu_chon = models.BooleanField(default=False, verbose_name="Là học phần tự chọn? (IsMHTN=1)")
    khong_tinh_diem_tb = models.BooleanField(default=False, verbose_name="Không tính ĐTB? (KhgTinhDTB=1)")

    mo_ta_hoc_phan = models.TextField(blank=True, null=True, verbose_name="Mô tả chung học phần")
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo bản ghi")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật bản ghi")
    
    @property
    def tong_so_tin_chi_tinh_toan(self):
        # Đổi tên property để tránh trùng với trường tong_so_tin_chi_goc
        return (self.tin_chi_ly_thuyet_goc or 0) + (self.tin_chi_thuc_hanh_goc or 0)

    def __str__(self):
        return f"{self.ma_hoc_phan} - {self.ten_hoc_phan}"

    class Meta:
        verbose_name = "Học phần (Thư viện chung)"
        verbose_name_plural = "Các Học phần (Thư viện chung)"
        ordering = ['ma_hoc_phan']

# 2. Model ChuongTrinhDaoTao - Cập nhật để dùng ManyToManyField với HocPhan
# (Các import và các model DonViDaoTao, NganhDaoTao, DanhMucKienThuc, HocPhan, ChiTietHocPhanTrongCTDT đã có)

class ChuongTrinhDaoTao(models.Model):
    TRINH_DO_CHOICES = [
        ('DH', 'Đại học'), 
        ('CD', 'Cao đẳng'),
        ('THS', 'Thạc sĩ'), 
        ('TS', 'Tiến sĩ'),
    ]
    HINH_THUC_CHOICES = [
        ('CQ', 'Chính quy'), 
        ('VLVH', 'Vừa làm vừa học'), 
        ('TX', 'Từ xa'),
    ]
    VAN_BANG_CHOICES = [ # Thêm lựa chọn cho văn bằng
        ('CN', 'Cử nhân'),
        ('KS', 'Kỹ sư'),
        ('BS', 'Bác sĩ'),
        # Thêm các loại văn bằng khác nếu cần
    ]

    # Thông tin định danh chương trình
    ma_nganh_ctdt = models.CharField(max_length=20, unique=True, verbose_name="Mã chương trình/ngành đào tạo") # Mã của CTĐT cụ thể
    ten_nganh_ctdt = models.CharField(max_length=255, verbose_name="Tên chương trình đào tạo (Tiếng Việt)")
    ten_tieng_anh = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên chương trình đào tạo (Tiếng Anh)")

    # Liên kết với Ngành học chung (từ model NganhDaoTao - danh mục)
    nganh_hoc_chung = models.ForeignKey(
        NganhDaoTao, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Thuộc Ngành học (chung)"
    )
    
    trinh_do_dao_tao = models.CharField(
        max_length=3,
        choices=TRINH_DO_CHOICES,
        default='DH', # Đổi default sang Đại học cho phù hợp với ví dụ mới
        verbose_name="Trình độ đào tạo"
    )
    hinh_thuc_dao_tao = models.CharField(
        max_length=4,
        choices=HINH_THUC_CHOICES,
        default='CQ',
        verbose_name="Hình thức đào tạo"
    )
    
    # Các thông tin tổng quát khác
    so_tin_chi_yeu_cau = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tổng số tín chỉ yêu cầu")
    thoi_gian_dao_tao = models.CharField(max_length=50, blank=True, verbose_name="Thời gian đào tạo (ví dụ: 3.5 năm)")
    doi_tuong_tuyen_sinh = models.TextField(blank=True, null=True, verbose_name="Đối tượng tuyển sinh")
    dieu_kien_tot_nghiep = models.TextField(blank=True, null=True, verbose_name="Điều kiện tốt nghiệp")
    van_bang_tot_nghiep = models.CharField(
        max_length=3, 
        choices=VAN_BANG_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name="Văn bằng tốt nghiệp"
    )
    chuong_trinh_tham_khao = models.TextField(blank=True, null=True, verbose_name="Chương trình đào tạo tham khảo")
    
    don_vi_quan_ly = models.ForeignKey(
        DonViDaoTao, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Đơn vị quản lý"
    )
    mo_ta_chung = models.TextField(blank=True, null=True, verbose_name="Mô tả chung CTĐT")
    
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    hoc_phan_trong_chuong_trinh = models.ManyToManyField(
        HocPhan,
        through='ChiTietHocPhanTrongCTDT',
        through_fields=('chuong_trinh_dao_tao', 'hoc_phan'),
        related_name='co_trong_cac_ctdt',
        verbose_name="Các học phần trong chương trình"
    )

    def __str__(self):
        return f"{self.ten_nganh_ctdt} ({self.ma_nganh_ctdt}) - {self.get_trinh_do_dao_tao_display()}"

    class Meta:
        verbose_name = "Chương trình Đào tạo"
        verbose_name_plural = "Các Chương trình Đào tạo"
        ordering = ['ten_nganh_ctdt']

# (Các import và các model khác đã có)


# Model MucTieuDaoTao - Mục tiêu đào tạo của CTĐT (PO)

class MucTieuDaoTao(models.Model):
    chuong_trinh_dao_tao = models.ForeignKey(
    ChuongTrinhDaoTao,
    on_delete=models.CASCADE,
    related_name='muc_tieu_dao_tao_ctdt',
    verbose_name="Chương trình đào tạo"
    )
    ma_muc_tieu = models.CharField(max_length=20, verbose_name="Mã mục tiêu (PO)")
    noi_dung = models.TextField(verbose_name="Nội dung mục tiêu đào tạo")

    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    def __str__(self):
        # Cách hiển thị hiện tại có thể chưa đủ rõ, ví dụ nếu nó là:
        # return f"MucTieuDaoTao object ({self.pk})" 
        # HOẶC nếu nó chỉ là self.ma_muc_tieu mà mã mục tiêu không đủ để nhớ
        
        # Hãy thử cách hiển thị tốt hơn:
        return f"{self.ma_muc_tieu}: {self.noi_dung[:60]}..." # Hiển thị mã và một phần nội dung
        # Hoặc nếu mã mục tiêu đã đủ rõ ràng:
        # return self.ma_muc_tieu 
        # Hoặc kết hợp cả mã và tên chương trình nếu cần phân biệt PO của các CTĐT khác nhau (mặc dù ở đây là PO của CTĐT đã chọn)
        # return f"{self.chuong_trinh_dao_tao.ma_nganh_ctdt} - {self.ma_muc_tieu}"
    class Meta:
        verbose_name = "Mục tiêu Đào tạo CTĐT (PO)"
        verbose_name_plural = "Các Mục tiêu Đào tạo CTĐT (PO)"

class ChuanDauRa(models.Model):
    LOAI_CDR_CHOICES = [
        ('KT', 'Về kiến thức'),
        ('KN', 'Về kỹ năng'),
        ('TD', 'Về thái độ/Năng lực tự chủ và trách nhiệm'),
        ('KHAC', 'Khác'),
    ]
    # Bạn có thể thêm MUC_DO_NANG_LUC_CHOICES nếu cần

    chuong_trinh_dao_tao = models.ForeignKey(
        ChuongTrinhDaoTao,
        on_delete=models.CASCADE,
        related_name='chuan_dau_ra_ctdt',
        verbose_name="Chương trình đào tạo"
    )
    ma_cdr = models.CharField(max_length=20, verbose_name="Mã chuẩn đầu ra (PLO)")
    noi_dung = models.TextField(verbose_name="Nội dung chuẩn đầu ra")
    loai_cdr = models.CharField(
        max_length=5,
        choices=LOAI_CDR_CHOICES,
        blank=True, null=True,
        verbose_name="Loại chuẩn đầu ra"
    )
    # muc_do_nang_luc = models.CharField(max_length=.., choices=MUC_DO_NANG_LUC_CHOICES, ...) 
    dap_ung_muc_tieu = models.ManyToManyField(
        MucTieuDaoTao,
        related_name='cac_cdr_dap_ung',
        blank=True, # Một CĐR có thể không đáp ứng trực tiếp PO nào hoặc nhiều PO
        verbose_name="Đáp ứng Mục tiêu Đào tạo (PO)"
    )
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    def __str__(self):
        return f"{self.ma_cdr} - {self.chuong_trinh_dao_tao.ten_nganh_ctdt}"

    class Meta:
        verbose_name = "Chuẩn Đầu Ra CTĐT (PLO)"
        verbose_name_plural = "Các Chuẩn Đầu Ra CTĐT (PLO)"
        unique_together = [['chuong_trinh_dao_tao', 'ma_cdr']]
        ordering = ['chuong_trinh_dao_tao', 'ma_cdr']
# 3. **THÊM MODEL TRUNG GIAN ChiTietHocPhanTrongCTDT**
# (Các import và các model khác đã có)

class ChiTietHocPhanTrongCTDT(models.Model):
    chuong_trinh_dao_tao = models.ForeignKey(ChuongTrinhDaoTao, on_delete=models.CASCADE, verbose_name="Chương trình đào tạo")
    hoc_phan = models.ForeignKey(HocPhan, on_delete=models.CASCADE, verbose_name="Học phần (từ thư viện)")
    
    danh_muc_kien_thuc = models.ForeignKey(
        DanhMucKienThuc, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Phân loại trong CTĐT này"
    )
    la_bat_buoc = models.BooleanField(default=True, verbose_name="Bắt buộc trong CTĐT này?")
    hoc_ky_du_kien = models.PositiveIntegerField(null=True, blank=True, verbose_name="Học kỳ dự kiến")
    
    tin_chi_ly_thuyet_apdung = models.PositiveIntegerField(null=True, blank=True, verbose_name="Số TC LT áp dụng")
    tin_chi_thuc_hanh_apdung = models.PositiveIntegerField(null=True, blank=True, verbose_name="Số TC TH áp dụng")
    so_gio_ly_thuyet_apdung = models.PositiveIntegerField(null=True, blank=True, verbose_name="Số giờ LT áp dụng")
    so_gio_thuc_hanh_apdung = models.PositiveIntegerField(null=True, blank=True, verbose_name="Số giờ TH áp dụng")
    so_gio_tu_hoc_apdung = models.PositiveIntegerField(null=True, blank=True, verbose_name="Số giờ tự học áp dụng")

    # THÊM TRƯỜNG MỚI CHO SỐ TIẾT ONLINE
    so_tiet_ly_thuyet_online = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name="Số tiết Lý thuyết Online") 
    # Để blank=True, null=True để không bắt buộc nhập ngay và tương thích với dữ liệu cũ có thể chưa có thông tin này

    ghi_chu_trong_ctdt = models.TextField(blank=True, null=True, verbose_name="Ghi chú riêng cho CTĐT")

    ngay_tao_lien_ket = models.DateTimeField(auto_now_add=True, verbose_name="Ngày thêm vào CTĐT")
    ngay_cap_nhat_lien_ket = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật trong CTĐT")

    @property
    def tong_so_tin_chi_apdung(self):
        lt = self.tin_chi_ly_thuyet_apdung if self.tin_chi_ly_thuyet_apdung is not None else (self.hoc_phan.tin_chi_ly_thuyet_goc if self.hoc_phan else 0)
        th = self.tin_chi_thuc_hanh_apdung if self.tin_chi_thuc_hanh_apdung is not None else (self.hoc_phan.tin_chi_thuc_hanh_goc if self.hoc_phan else 0)
        return (lt or 0) + (th or 0)

    def __str__(self):
        hoc_phan_ten = self.hoc_phan.ten_hoc_phan if self.hoc_phan else "Học phần không xác định"
        ctdt_ten = self.chuong_trinh_dao_tao.ten_nganh_ctdt if self.chuong_trinh_dao_tao else "CTĐT không xác định"
        return f"{hoc_phan_ten} trong {ctdt_ten} ({self.tong_so_tin_chi_apdung} TC áp dụng)"

    class Meta:
        verbose_name = "Chi tiết Học phần trong CTĐT"
        verbose_name_plural = "Các Chi tiết Học phần trong CTĐT"
        unique_together = [['chuong_trinh_dao_tao', 'hoc_phan']]
        ordering = ['chuong_trinh_dao_tao', 'hoc_phan__ma_hoc_phan']


def str(self):
    return f"{self.ma_muc_tieu} - {self.chuong_trinh_dao_tao.ten_nganh_ctdt}"

class Meta:
    verbose_name = "Mục tiêu Đào tạo CTĐT (PO)"
    verbose_name_plural = "Các Mục tiêu Đào tạo CTĐT (PO)"
    unique_together = [['chuong_trinh_dao_tao', 'ma_muc_tieu']]
    ordering = ['chuong_trinh_dao_tao', 'ma_muc_tieu']


# Model DeCuongHocPhan - Đề cương học phần

class DeCuongHocPhan(models.Model):
    hoc_phan = models.ForeignKey(
        HocPhan, 
        on_delete=models.CASCADE, 
        related_name='cac_de_cuong',
        verbose_name="Học phần"
    )
    # ten_de_cuong có thể giữ để người dùng đặt tên gợi nhớ cho phiên bản, vd: "ĐC áp dụng HK1 2025-2026"
    ten_de_cuong_phien_ban = models.CharField(max_length=255, verbose_name="Tên/Ghi chú cho phiên bản đề cương này")
    so_phien_ban = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số hiệu phiên bản (nếu có)")
    ngay_ban_hanh = models.DateField(verbose_name="Ngày ban hành/Hiệu lực")
    ly_do_cap_nhat = models.TextField(blank=True, null=True, verbose_name="Lý do cập nhật/Nội dung thay đổi chính")
    # nguoi_cap_nhat = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người cập nhật") # Nếu cần liên kết với User Django

    la_phien_ban_hien_hanh = models.BooleanField(
        default=False, # Chỉ một phiên bản nên là True cho mỗi học phần
        verbose_name="Là phiên bản hiện hành?"
    )
    
    # Nội dung chi tiết của phiên bản đề cương này
    muc_tieu_hoc_phan = models.TextField(blank=True, null=True, verbose_name="Mục tiêu học phần (của phiên bản này)")
    tom_tat_noi_dung = models.TextField(blank=True, null=True, verbose_name="Tóm tắt nội dung học phần")
    phuong_phap_day_hoc = models.TextField(blank=True, null=True, verbose_name="Phương pháp dạy và học")
    nhiem_vu_sinh_vien = models.TextField(blank=True, null=True, verbose_name="Nhiệm vụ của sinh viên")
    thang_diem_danh_gia = models.TextField(blank=True, null=True, verbose_name="Thang điểm/Cách đánh giá")
    tai_lieu_hoc_tap = models.TextField(blank=True, null=True, verbose_name="Tài liệu học tập")
    
    ngay_tao_record = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo bản ghi") # Đổi tên để phân biệt
    ngay_cap_nhat_record = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật bản ghi") # Đổi tên

    def save(self, *args, **kwargs):
        # Đảm bảo chỉ có một phiên bản hiện hành cho mỗi học phần
        if self.la_phien_ban_hien_hanh:
            DeCuongHocPhan.objects.filter(hoc_phan=self.hoc_phan).exclude(pk=self.pk).update(la_phien_ban_hien_hanh=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Đề cương HP: {self.hoc_phan.ten_hoc_phan} - Phiên bản: {self.ten_de_cuong_phien_ban or self.ngay_ban_hanh.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Phiên bản Đề cương Học phần"
        verbose_name_plural = "Các Phiên bản Đề cương Học phần"
        ordering = ['hoc_phan', '-ngay_ban_hanh']
        # unique_together = [['hoc_phan', 'so_phien_ban']] # Nếu so_phien_ban là duy nhất

class ChuanDauRaHocPhan(models.Model):
    MUC_DO_BLOOM_CHOICES = [
        ('REM', 'Nhận biết (Remembering)'),
        ('UND', 'Thông hiểu (Understanding)'),
        ('APP', 'Vận dụng (Applying)'),
        ('ANA', 'Phân tích (Analyzing)'),
        ('EVA', 'Đánh giá (Evaluating)'),
        ('CRE', 'Sáng tạo (Creating)'),
    ]
    # THÊM LOAI_CLO_CHOICES VÀO ĐÂY
    LOAI_CLO_CHOICES = [
        ('KT', 'Kiến thức'),
        ('KN', 'Kỹ năng'),
        ('TD', 'Thái độ/Năng lực tự chủ và trách nhiệm'),
        ('KHAC', 'Khác'),
    ]

    de_cuong = models.ForeignKey(
        DeCuongHocPhan, 
        on_delete=models.CASCADE, 
        related_name='chuan_dau_ra_cua_de_cuong',
        verbose_name="Thuộc Đề cương học phần"
    )
    ma_clo = models.CharField(max_length=20, verbose_name="Mã Chuẩn đầu ra học phần (CLO)")
    noi_dung = models.TextField(verbose_name="Nội dung Chuẩn đầu ra học phần")
    
    dong_tu_bloom = models.CharField(max_length=100, blank=True, null=True, verbose_name="Động từ Bloom chính")
    muc_do_bloom = models.CharField(
        max_length=3,
        choices=MUC_DO_BLOOM_CHOICES,
        blank=True, null=True,
        verbose_name="Mức độ theo thang Bloom"
    )
    
    # THÊM TRƯỜNG loai_clo VÀO ĐÂY
    loai_clo = models.CharField(
        max_length=5, # Đủ để chứa 'KHAC'
        choices=LOAI_CLO_CHOICES,
        blank=True, null=True,
        verbose_name="Loại Chuẩn đầu ra học phần"
    )

    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    def __str__(self):
        return f"{self.ma_clo} ({self.de_cuong.hoc_phan.ten_hoc_phan})"

    class Meta:
        verbose_name = "Chuẩn Đầu Ra Học Phần (CLO)"
        verbose_name_plural = "Các Chuẩn Đầu Ra Học Phần (CLO)"
        unique_together = [['de_cuong', 'ma_clo']]
        ordering = ['de_cuong', 'ma_clo']




# Model MaTranCDR_CTHP - Ma trận chuẩn đầu ra của học phần trong CTĐT
class MaTranCDR_CTHP(models.Model):
    chuan_dau_ra = models.ForeignKey(ChuanDauRa, on_delete=models.CASCADE)
    chi_tiet_hoc_phan = models.ForeignKey(ChiTietHocPhanTrongCTDT, on_delete=models.CASCADE)
    muc_do_dong_gop = models.CharField(max_length=1, choices=[('I','Introduced'),('R','Reinforced'),('M','Mastery')], blank=True, null=True)
    # Các thông tin khác nếu cần

    class Meta:
        verbose_name = "Ma trận CĐR CTĐT - Học phần"
        verbose_name_plural = "Các Ma trận CĐR CTĐT - Học phần"
        unique_together = [['chuan_dau_ra', 'chi_tiet_hoc_phan']]