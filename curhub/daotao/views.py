from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q, OuterRef, Exists
from django.contrib import messages
from .forms import (
    NganhDaoTaoForm, ChuongTrinhDaoTaoModelForm, HocPhanLibModelForm,
    ChiTietHocPhanTrongCTDTModelForm, DonViDaoTaoForm, MucTieuDaoTaoFormSet,
    ChuanDauRaFormSet, UploadHocPhanCTDTForm, ChuanDauRaForm, MucTieuDaoTaoForm
)
from .models import (
    NganhDaoTao, ChuongTrinhDaoTao, HocPhan, ChiTietHocPhanTrongCTDT,
    LichSuThayDoiCTDT, DonViDaoTao, MucTieuDaoTao, ChuanDauRa
)
from django.db import transaction 
import pandas as pd
import io

def index(request):
    return redirect('daotao:danh_sach_ctdt')

def them_nganh_dao_tao(request):
    if request.method == 'POST':
        form = NganhDaoTaoForm(request.POST)
        if form.is_valid():
            form.save()
            form = NganhDaoTaoForm()
            return render(request, 'daotao/them_nganh.html', {
                'form': form,
                'message': 'Đã thêm ngành đào tạo thành công!'
            })
    else:
        form = NganhDaoTaoForm()
    context = {'form': form}
    return render(request, 'daotao/them_nganh.html', context)

def them_chuong_trinh_dao_tao(request):
    if request.method == 'POST':
        form = ChuongTrinhDaoTaoModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm Chương trình Đào tạo thành công!')
            form = ChuongTrinhDaoTaoModelForm() # Reset form for new entry
        else:
            messages.error(request, 'Có lỗi xảy ra khi thêm Chương trình Đào tạo. Vui lòng kiểm tra lại các trường.')
    else:
        form = ChuongTrinhDaoTaoModelForm()
    context = {
        'form': form,
        'page_title': 'Thêm Chương Trình Đào Tạo Mới'
    }
    return render(request, 'daotao/them_ctdt.html', context)

def danh_sach_ctdt(request):
    chuong_trinh_list = ChuongTrinhDaoTao.objects.prefetch_related('hoc_phan_trong_chuong_trinh').order_by('-ngay_cap_nhat')
    query_search = request.GET.get('q', '')
    trang_thai_filter = request.GET.get('trang_thai', '')
    don_vi_filter = request.GET.get('don_vi', '')
    if query_search:
        chuong_trinh_list = chuong_trinh_list.filter(
            Q(ten_nganh_ctdt__icontains=query_search) |
            Q(ma_nganh_ctdt__icontains=query_search)
        )
    if trang_thai_filter:
        chuong_trinh_list = chuong_trinh_list.filter(trang_thai=trang_thai_filter)
    if don_vi_filter:
        chuong_trinh_list = chuong_trinh_list.filter(don_vi_quan_ly__id=don_vi_filter)
    paginator = Paginator(chuong_trinh_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'TRANG_THAI_CHOICES': ChuongTrinhDaoTao.TRANG_THAI_CHOICES,
        'don_vi_list': DonViDaoTao.objects.all(),
        'query_search': query_search,
        'trang_thai_filter': trang_thai_filter,
        'don_vi_filter': don_vi_filter,
    }
    return render(request, 'daotao/danh_sach_ctdt.html', context)

def chi_tiet_ctdt(request, pk_ctdt):
    chuong_trinh = get_object_or_404(ChuongTrinhDaoTao, pk=pk_ctdt)
    hoc_phan_trong_ctdt = ChiTietHocPhanTrongCTDT.objects.filter(
        chuong_trinh_dao_tao=chuong_trinh
    ).order_by('hoc_ky_du_kien', 'hoc_phan__ma_hoc_phan')
    muc_tieu_dao_tao_ctdt = MucTieuDaoTao.objects.filter(chuong_trinh_dao_tao=chuong_trinh).order_by('ma_muc_tieu')
    chuan_dau_ra_ctdt = ChuanDauRa.objects.filter(chuong_trinh_dao_tao=chuong_trinh).prefetch_related('dap_ung_muc_tieu').order_by('loai_cdr', 'ma_cdr')

    # Group PLOs by type for the matrix display
    plo_groups = {}
    for plo in chuan_dau_ra_ctdt:
        group_name = plo.get_loai_cdr_display()
        if group_name not in plo_groups:
            plo_groups[group_name] = []
        
        # Create a set of related PO pks for quick lookup in the template
        plo.related_pos_pks = set(po.pk for po in plo.dap_ung_muc_tieu.all())
        plo_groups[group_name].append(plo)

    context = {
        'ctdt': chuong_trinh,
        'page_title': f"Chi tiết CTĐT: {chuong_trinh.ten_nganh_ctdt}",
        'hoc_phan_trong_ctdt': hoc_phan_trong_ctdt,
        'muc_tieu_dao_tao_ctdt': muc_tieu_dao_tao_ctdt,
        'chuan_dau_ra_ctdt': chuan_dau_ra_ctdt, # Keep for simple list if needed elsewhere
        'plo_groups': plo_groups,
    }
    return render(request, 'daotao/chi_tiet_ctdt.html', context)

@login_required
def sua_ctdt(request, pk_ctdt):
    ctdt = get_object_or_404(ChuongTrinhDaoTao, pk=pk_ctdt)
    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể sửa CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=pk_ctdt)
    if request.method == 'POST':
        form = ChuongTrinhDaoTaoModelForm(request.POST, instance=ctdt)
        po_formset = MucTieuDaoTaoFormSet(request.POST, instance=ctdt, prefix='po')
        plo_formset = ChuanDauRaFormSet(request.POST, instance=ctdt, prefix='plo')
        if form.is_valid() and po_formset.is_valid() and plo_formset.is_valid():
            with transaction.atomic():
                form.save()
                po_formset.save()
                plo_formset.save()
            messages.success(request, "Đã cập nhật Chương trình Đào tạo và các mục liên quan thành công!")
            return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.id)
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật. Vui lòng kiểm tra lại các trường.")
    else:
        form = ChuongTrinhDaoTaoModelForm(instance=ctdt)
        po_formset = MucTieuDaoTaoFormSet(instance=ctdt, prefix='po')
        plo_formset = ChuanDauRaFormSet(instance=ctdt, prefix='plo')
    hoc_phan_trong_ctdt = ChiTietHocPhanTrongCTDT.objects.filter(
        chuong_trinh_dao_tao=ctdt
    ).order_by('hoc_ky_du_kien', 'hoc_phan__ma_hoc_phan')
    context = {
        'form': form,
        'ctdt': ctdt,
        'po_formset': po_formset,
        'plo_formset': plo_formset,
        'hoc_phan_trong_ctdt': hoc_phan_trong_ctdt,
        'page_title': f'Cập nhật Chương trình: {ctdt.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/sua_ctdt.html', context)

@login_required
def xoa_ctdt(request, pk_ctdt):
    chuong_trinh_can_xoa = get_object_or_404(ChuongTrinhDaoTao, pk=pk_ctdt)
    if request.method == 'POST':
        chuong_trinh_can_xoa.delete()
        messages.success(request, f"Đã xóa chương trình đào tạo '{chuong_trinh_can_xoa.ten_nganh_ctdt}' thành công.")
        return redirect('daotao:danh_sach_ctdt')
    context = {
        'ctdt': chuong_trinh_can_xoa,
        'page_title': f'Xác nhận Xóa CTĐT: {chuong_trinh_can_xoa.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/xoa_ctdt_confirm.html', context)

def danh_sach_hoc_phan(request):
    hoc_phan_list = HocPhan.objects.select_related('don_vi_quan_ly_goc').order_by('ma_hoc_phan')
    
    # Lấy các tham số từ query string
    query_search = request.GET.get('q', '')
    don_vi_filter = request.GET.get('don_vi', '')
    
    # Lọc theo query search
    if query_search:
        hoc_phan_list = hoc_phan_list.filter(
            Q(ma_hoc_phan__icontains=query_search) |
            Q(ten_hoc_phan__icontains=query_search)
        )
        
    # Lọc theo đơn vị quản lý
    if don_vi_filter:
        hoc_phan_list = hoc_phan_list.filter(don_vi_quan_ly_goc__id=don_vi_filter)

    paginator = Paginator(hoc_phan_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách đơn vị để hiển thị trong bộ lọc
    don_vi_list = DonViDaoTao.objects.all()
    
    context = {
        'page_obj': page_obj,
        'page_title': 'Danh Sách Học Phần',
        'don_vi_list': don_vi_list,
        'query_search': query_search,
        'don_vi_filter': don_vi_filter,
    }
    return render(request, 'daotao/danh_sach_hoc_phan.html', context)

@login_required
def them_hoc_phan_hang_loat(request, pk_ctdt):
    ctdt = get_object_or_404(ChuongTrinhDaoTao, pk=pk_ctdt)
    if request.method == 'GET' and request.GET.get('format') == 'datatables':
        try:
            draw = int(request.GET.get('draw', 1))
            start = int(request.GET.get('start', 0))
            length = int(request.GET.get('length', 10))
            search_ma_hp = request.GET.get('search_ma_hp', '')
            search_ten_hp = request.GET.get('search_ten_hp', '')
            search_don_vi_ql = request.GET.get('search_don_vi_ql', '')
            queryset = HocPhan.objects.select_related('don_vi_quan_ly_goc').order_by('ma_hoc_phan')
            total_records = queryset.count()
            if search_ma_hp:
                queryset = queryset.filter(ma_hoc_phan__icontains=search_ma_hp)
            if search_ten_hp:
                queryset = queryset.filter(ten_hoc_phan__icontains=search_ten_hp)
            if search_don_vi_ql:
                queryset = queryset.filter(don_vi_quan_ly_goc__pk=search_don_vi_ql)
            filtered_records = queryset.count()
            paginated_queryset = queryset[start:start + length]
            existing_hp_pks_set = set(ChiTietHocPhanTrongCTDT.objects.filter(
                chuong_trinh_dao_tao=ctdt
            ).values_list('hoc_phan__pk', flat=True))
            data = []
            for hp in paginated_queryset:
                try:
                    is_disabled = hp.pk in existing_hp_pks_set
                    checkbox_html = f'''
                        <input type="checkbox" name="selected_hoc_phan" value="{hp.pk}" class="hoc-phan-checkbox"
                        {'disabled' if is_disabled else ''} title="{'Học phần này đã có trong CTĐT' if is_disabled else ''}">
                    '''
                    hoc_ky_input_html = f'<input type="number" name="hoc_ky" class="form-control form-control-sm" style="width: 60px;">'
                    don_vi_name = hp.don_vi_quan_ly_goc.ten_don_vi if hp.don_vi_quan_ly_goc else "N/A"
                    mo_ta_text = hp.mo_ta_hoc_phan or ""
                    mo_ta_display = mo_ta_text[:100] + '...' if len(mo_ta_text) > 100 else mo_ta_text
                    data.append([
                        checkbox_html,
                        hp.ma_hoc_phan,
                        hp.ten_hoc_phan,
                        hp.tong_so_tin_chi_goc,
                        don_vi_name,
                        mo_ta_display,
                        hoc_ky_input_html
                    ])
                except Exception as e:
                    error_message = f"Lỗi xử lý HP ID {hp.pk}: {str(e)}"
                    data.append([
                        f'<input type="checkbox" disabled title="{error_message}">',
                        hp.ma_hoc_phan,
                        hp.ten_hoc_phan,
                        "Lỗi",
                        "Lỗi",
                        error_message
                    ])
            response_data = {
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": filtered_records,
                "data": data
            }
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({"error": str(e), "data": [], "recordsFiltered": 0, "recordsTotal": 0}, status=500)
    if request.method == 'POST':
        selected_hoc_phan_pks = request.POST.getlist('selected_hoc_phan')
        hoc_ky_du_kien_default = request.POST.get('hoc_ky_du_kien_default')
        la_bat_buoc_default_str = request.POST.get('la_bat_buoc_default')
        success_count = 0
        error_count = 0
        errors = []
        try:
            hoc_ky_du_kien_default = int(hoc_ky_du_kien_default) if hoc_ky_du_kien_default else None
        except (ValueError, TypeError):
            hoc_ky_du_kien_default = None
        la_bat_buoc_default = None
        if la_bat_buoc_default_str == 'True':
            la_bat_buoc_default = True
        elif la_bat_buoc_default_str == 'False':
            la_bat_buoc_default = False
        for hp_pk in selected_hoc_phan_pks:
            try:
                if ChiTietHocPhanTrongCTDT.objects.filter(chuong_trinh_dao_tao=ctdt, hoc_phan_id=hp_pk).exists():
                    errors.append(f"Học phần PK '{hp_pk}' đã tồn tại.")
                    error_count += 1
                    continue
                hoc_phan_obj = HocPhan.objects.get(pk=hp_pk)
                chi_tiet_hp_data = {
                    'chuong_trinh_dao_tao': ctdt.pk,
                    'hoc_phan': hoc_phan_obj.pk,
                    'tin_chi_ly_thuyet_apdung': hoc_phan_obj.tin_chi_ly_thuyet_goc,
                    'tin_chi_thuc_hanh_apdung': hoc_phan_obj.tin_chi_thuc_hanh_goc,
                }
                hoc_ky = request.POST.get(f'hoc_ky_{hp_pk}')
                if hoc_ky:
                    chi_tiet_hp_data['hoc_ky_du_kien'] = int(hoc_ky)
                elif hoc_ky_du_kien_default is not None:
                    chi_tiet_hp_data['hoc_ky_du_kien'] = hoc_ky_du_kien_default
                if la_bat_buoc_default is not None:
                    chi_tiet_hp_data['la_bat_buoc'] = la_bat_buoc_default
                # Create a form instance without the excluded fields
                form_instance = ChiTietHocPhanTrongCTDTModelForm(data=chi_tiet_hp_data)
                if form_instance.is_valid():
                    # Create the instance without saving to the DB
                    chi_tiet_instance = form_instance.save(commit=False)
                    # Set the excluded fields
                    chi_tiet_instance.chuong_trinh_dao_tao = ctdt
                    chi_tiet_instance.hoc_phan = hoc_phan_obj
                    # Save the instance to the DB
                    chi_tiet_instance.save()
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"Lỗi HP PK '{hp_pk}': {form_instance.errors.as_text()}")
            except Exception as e:
                error_count += 1
                errors.append(f"Lỗi không xác định với HP PK '{hp_pk}': {e}")
        if success_count > 0:
            messages.success(request, f"Đã thêm thành công {success_count} học phần.")
        if error_count > 0:
            messages.error(request, f"Có {error_count} lỗi: " + " | ".join(errors))
        return redirect(f"{reverse('daotao:chi_tiet_ctdt', kwargs={'pk_ctdt': ctdt.pk})}#hocphan-tab-pane")
    if not HocPhan.objects.exists():
        messages.warning(request, "Thư viện học phần trống. Vui lòng thêm học phần vào thư viện trước khi thực hiện chức năng này.")
    context = {
        'ctdt': ctdt,
        'page_title': f'Thêm Học Phần Hàng Loạt cho CTĐT: {ctdt.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/them_hoc_phan_hang_loat.html', context)

@login_required
def upload_hoc_phan_ctdt(request, pk_ctdt):
    ctdt = get_object_or_404(ChuongTrinhDaoTao, pk=pk_ctdt)
    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể upload học phần khi CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=pk_ctdt)
    if request.method == 'POST':
        form = UploadHocPhanCTDTForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = None
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(io.TextIOWrapper(file.file, encoding='utf-8'))
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file.file)
                else:
                    messages.error(request, "Định dạng tệp không được hỗ trợ. Vui lòng tải lên tệp .xlsx hoặc .csv.")
                    return redirect('daotao:upload_hoc_phan_ctdt', pk_ctdt=pk_ctdt)
            except Exception as e:
                messages.error(request, f"Lỗi đọc tệp: {e}. Vui lòng kiểm tra định dạng và nội dung tệp.")
                return redirect('daotao:upload_hoc_phan_ctdt', pk_ctdt=pk_ctdt)
            if df is not None:
                success_count = 0
                error_count = 0
                errors = []
                column_mapping = {
                    'Mã học phần': 'ma_hoc_phan', 'Tên học phần': 'ten_hoc_phan', 'Tên học phần (TA)': 'ten_hoc_phan_tieng_anh',
                    'Tổng TC': 'tong_so_tin_chi_goc', 'TC LT': 'tin_chi_ly_thuyet_goc', 'TC TH': 'tin_chi_thuc_hanh_goc',
                    'Số giờ LT': 'so_gio_ly_thuyet_goc', 'Số giờ TH': 'so_gio_thuc_hanh_goc', 'Số giờ Tự học': 'so_gio_tu_hoc_goc',
                    'Đơn vị QL': 'don_vi_quan_ly_goc_ma', 'Mô tả HP': 'mo_ta_hoc_phan', 'Tài liệu': 'tai_lieu_hoc_tap',
                    'Điều kiện tiên quyết': 'dieu_kien_tien_quyet', 'Điều kiện song hành': 'dieu_kien_song_hanh',
                    'Học phần tương đương': 'hoc_phan_tuong_duong', 'Học phần thay thế': 'hoc_phan_thay_the',
                    'Ghi chú HP': 'ghi_chu_hoc_phan', 'Học kỳ dự kiến': 'hoc_ky_du_kien', 'Là bắt buộc': 'la_bat_buoc',
                    'TC LT áp dụng': 'tin_chi_ly_thuyet_apdung', 'TC TH áp dụng': 'tin_chi_thuc_hanh_apdung',
                    'Số giờ LT áp dụng': 'so_gio_ly_thuyet_apdung', 'Số giờ TH áp dụng': 'so_gio_thuc_hanh_apdung',
                    'Số giờ Tự học áp dụng': 'so_gio_tu_hoc_apdung', 'Số tiết LT online': 'so_tiet_ly_thuyet_online',
                    'Ghi chú chi tiết HP': 'ghi_chu_chi_tiet_hp',
                }
                df.rename(columns=column_mapping, inplace=True)
                required_cols = ['ma_hoc_phan', 'ten_hoc_phan', 'tong_so_tin_chi_goc']
                if not all(col in df.columns for col in required_cols):
                    missing_cols = [col for col in required_cols if col not in df.columns]
                    messages.error(request, f"Tệp thiếu các cột bắt buộc: {', '.join(missing_cols)}. Vui lòng kiểm tra template.")
                    return redirect('daotao:upload_hoc_phan_ctdt', pk_ctdt=pk_ctdt)
                with transaction.atomic():
                    for index, row in df.iterrows():
                        try:
                            ma_hoc_phan = row.get('ma_hoc_phan')
                            ten_hoc_phan = row.get('ten_hoc_phan')
                            if not ma_hoc_phan or not ten_hoc_phan:
                                errors.append(f"Dòng {index+2}: Mã học phần hoặc Tên học phần trống. Bỏ qua.")
                                error_count += 1
                                continue
                            don_vi_ql_ma = row.get('don_vi_quan_ly_goc_ma')
                            don_vi_ql_obj = None
                            if pd.notna(don_vi_ql_ma):
                                try:
                                    don_vi_ql_obj = DonViDaoTao.objects.get(ma_don_vi=str(don_vi_ql_ma).strip())
                                except DonViDaoTao.DoesNotExist:
                                    errors.append(f"Dòng {index+2} (HP: {ma_hoc_phan}): Mã đơn vị quản lý '{don_vi_ql_ma}' không tồn tại. Bỏ qua.")
                                    error_count += 1
                                    continue
                            hoc_phan_data = {
                                'ma_hoc_phan': ma_hoc_phan, 'ten_hoc_phan': ten_hoc_phan, 'ten_hoc_phan_tieng_anh': row.get('ten_hoc_phan_tieng_anh'),
                                'tong_so_tin_chi_goc': row.get('tong_so_tin_chi_goc'), 'tin_chi_ly_thuyet_goc': row.get('tin_chi_ly_thuyet_goc'),
                                'tin_chi_thuc_hanh_goc': row.get('tin_chi_thuc_hanh_goc'), 'so_gio_ly_thuyet_goc': row.get('so_gio_ly_thuyet_goc'),
                                'so_gio_thuc_hanh_goc': row.get('so_gio_thuc_hanh_goc'), 'so_gio_tu_hoc_goc': row.get('so_gio_tu_hoc_goc'),
                                'don_vi_quan_ly_goc': don_vi_ql_obj, 'mo_ta_hoc_phan': row.get('mo_ta_hoc_phan'),
                                'tai_lieu_hoc_tap': row.get('tai_lieu_hoc_tap'), 'dieu_kien_tien_quyet': row.get('dieu_kien_tien_quyet'),
                                'dieu_kien_song_hanh': row.get('dieu_kien_song_hanh'), 'hoc_phan_tuong_duong': row.get('hoc_phan_tuong_duong'),
                                'hoc_phan_thay_the': row.get('hoc_phan_thay_the'), 'ghi_chu_hoc_phan': row.get('ghi_chu_hoc_phan'),
                            }
                            hoc_phan_data = {k: (v if pd.notna(v) else None) for k, v in hoc_phan_data.items()}
                            hoc_phan_obj, created = HocPhan.objects.update_or_create(ma_hoc_phan=ma_hoc_phan, defaults=hoc_phan_data)
                            if ChiTietHocPhanTrongCTDT.objects.filter(chuong_trinh_dao_tao=ctdt, hoc_phan=hoc_phan_obj).exists():
                                errors.append(f"Dòng {index+2} (HP: {ma_hoc_phan}): Học phần đã tồn tại trong CTĐT này. Bỏ qua.")
                                error_count += 1
                                continue
                            chi_tiet_hp_data = {
                                'chuong_trinh_dao_tao': ctdt, 'hoc_phan': hoc_phan_obj, 'hoc_ky_du_kien': row.get('hoc_ky_du_kien'),
                                'la_bat_buoc': row.get('la_bat_buoc', False), 'tin_chi_ly_thuyet_apdung': row.get('tin_chi_ly_thuyet_apdung'),
                                'tin_chi_thuc_hanh_apdung': row.get('tin_chi_thuc_hanh_apdung'), 'so_gio_ly_thuyet_apdung': row.get('so_gio_ly_thuyet_apdung'),
                                'so_gio_thuc_hanh_apdung': row.get('so_gio_thuc_hanh_apdung'), 'so_gio_tu_hoc_apdung': row.get('so_gio_tu_hoc_apdung'),
                                'so_tiet_ly_thuyet_online': row.get('so_tiet_ly_thuyet_online'), 'ghi_chu_chi_tiet_hp': row.get('ghi_chu_chi_tiet_hp'),
                            }
                            chi_tiet_hp_data = {k: (v if pd.notna(v) else None) for k, v in chi_tiet_hp_data.items()}
                            la_bat_buoc_val = chi_tiet_hp_data.get('la_bat_buoc')
                            if isinstance(la_bat_buoc_val, str):
                                chi_tiet_hp_data['la_bat_buoc'] = la_bat_buoc_val.lower() == 'true'
                            elif pd.isna(la_bat_buoc_val):
                                chi_tiet_hp_data['la_bat_buoc'] = False
                            ChiTietHocPhanTrongCTDT.objects.create(**chi_tiet_hp_data)
                            success_count += 1
                        except Exception as e:
                            errors.append(f"Dòng {index+2} (HP: {row.get('ma_hoc_phan', 'N/A')}): Lỗi - {e}")
                            error_count += 1
                if success_count > 0:
                    messages.success(request, f"Đã tải lên thành công {success_count} học phần vào CTĐT.")
                if error_count > 0:
                    messages.error(request, f"Có {error_count} lỗi khi tải lên: " + " | ".join(errors))
                return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.pk)
        else:
            messages.error(request, "Vui lòng chọn một tệp hợp lệ.")
    else:
        form = UploadHocPhanCTDTForm()
    return render(request, 'daotao/upload_hoc_phan_ctdt.html', {'form': form, 'ctdt': ctdt})

@login_required
def them_muc_tieu_dao_tao(request, pk_ctdt):
    ctdt = get_object_or_404(ChuongTrinhDaoTao, pk=pk_ctdt)
    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể thêm Mục tiêu đào tạo cho CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=pk_ctdt)
    if request.method == 'POST':
        form = MucTieuDaoTaoForm(request.POST)
        if form.is_valid():
            mt = form.save(commit=False)
            mt.chuong_trinh_dao_tao = ctdt
            mt.save()
            messages.success(request, "Đã thêm Mục tiêu đào tạo thành công!")
            return redirect(f"{reverse('daotao:chi_tiet_ctdt', kwargs={'pk_ctdt': ctdt.pk})}#po-tab-pane")
        else:
            messages.error(request, "Có lỗi xảy ra khi thêm Mục tiêu đào tạo. Vui lòng kiểm tra lại các trường.")
    else:
        form = MucTieuDaoTaoForm()
    context = {
        'form': form,
        'ctdt': ctdt,
        'page_title': f'Thêm Mục tiêu Đào tạo cho CTĐT: {ctdt.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/them_muc_tieu_dao_tao.html', context)

# --- PLACEHOLDER FUNCTIONS START ---

@login_required
def gui_duyet_ctdt(request, pk_ctdt):
    return HttpResponse(f"Chức năng gửi duyệt cho CTĐT {pk_ctdt} chưa được triển khai.")

@login_required
def xu_ly_duyet_ctdt(request, pk_ctdt, action):
    return HttpResponse(f"Chức năng xử lý duyệt ({action}) cho CTĐT {pk_ctdt} chưa được triển khai.")

@login_required
def tao_phien_ban_moi_ctdt(request, pk_ctdt):
    return HttpResponse(f"Chức năng tạo phiên bản mới cho CTĐT {pk_ctdt} chưa được triển khai.")

@login_required
def luu_tru_ctdt(request, pk_ctdt):
    return HttpResponse(f"Chức năng lưu trữ CTĐT {pk_ctdt} chưa được triển khai.")

@login_required
def sua_hoc_phan(request, pk_hoc_phan):
    hoc_phan = get_object_or_404(HocPhan, pk=pk_hoc_phan)
    if request.method == 'POST':
        form = HocPhanLibModelForm(request.POST, instance=hoc_phan)
        if form.is_valid():
            form.save()
            messages.success(request, f"Đã cập nhật học phần '{hoc_phan.ten_hoc_phan}' thành công!")
            return redirect('daotao:danh_sach_hoc_phan')
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật học phần. Vui lòng kiểm tra lại các trường.")
    else:
        form = HocPhanLibModelForm(instance=hoc_phan)
    context = {
        'form': form,
        'hoc_phan': hoc_phan,
        'page_title': f'Cập nhật Học phần: {hoc_phan.ten_hoc_phan}'
    }
    return render(request, 'daotao/sua_hoc_phan.html', context)

@login_required
def xoa_hoc_phan(request, pk_hoc_phan):
    hoc_phan_can_xoa = get_object_or_404(HocPhan, pk=pk_hoc_phan)
    if request.method == 'POST':
        hoc_phan_can_xoa.delete()
        messages.success(request, f"Đã xóa học phần '{hoc_phan_can_xoa.ten_hoc_phan}' thành công.")
        return redirect('daotao:danh_sach_hoc_phan')
    context = {
        'hoc_phan': hoc_phan_can_xoa,
        'page_title': f'Xác nhận Xóa Học phần: {hoc_phan_can_xoa.ten_hoc_phan}'
    }
    return render(request, 'daotao/xoa_hoc_phan_confirm.html', context)

@login_required
def download_hoc_phan_ctdt_template(request):
    return HttpResponse(f"Chức năng download template chưa được triển khai.")

@login_required
def danh_sach_hoc_phan_theo_ctdt(request, pk_ctdt):
    return HttpResponse(f"Chức năng danh sách học phần theo ctdt {pk_ctdt} chưa được triển khai.")

@login_required
def them_hoc_phan_vao_ctdt(request, pk_ctdt):
    return HttpResponse(f"Chức năng thêm học phần vào ctdt {pk_ctdt} chưa được triển khai.")

@login_required
def chi_tiet_hoc_phan_trong_ctdt(request, pk_chi_tiet_hp):
    return HttpResponse(f"Chức năng chi tiết học phần trong ctdt {pk_chi_tiet_hp} chưa được triển khai.")

@login_required
def sua_chi_tiet_hp_trong_ctdt(request, pk_chi_tiet_hp):
    chi_tiet = get_object_or_404(ChiTietHocPhanTrongCTDT, pk=pk_chi_tiet_hp)
    ctdt = chi_tiet.chuong_trinh_dao_tao

    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể sửa chi tiết học phần cho CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.pk)

    if request.method == 'POST':
        form = ChiTietHocPhanTrongCTDTModelForm(request.POST, instance=chi_tiet)
        if form.is_valid():
            form.save()
            messages.success(request, f"Đã cập nhật chi tiết cho học phần: {chi_tiet.hoc_phan.ten_hoc_phan}")
            return redirect(f"{reverse('daotao:chi_tiet_ctdt', kwargs={'pk_ctdt': ctdt.pk})}#hocphan-tab-pane")
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật. Vui lòng kiểm tra lại các trường.")
    else:
        form = ChiTietHocPhanTrongCTDTModelForm(instance=chi_tiet)

    context = {
        'form': form,
        'ctdt': ctdt,
        'chi_tiet': chi_tiet,
        'page_title': f'Cập nhật Chi tiết Học phần: {chi_tiet.hoc_phan.ten_hoc_phan}'
    }
    return render(request, 'daotao/sua_chi_tiet_hp_trong_ctdt.html', context)

@login_required
def sua_hoc_phan_ctdt(request, pk_chi_tiet_hp):
    chi_tiet = get_object_or_404(ChiTietHocPhanTrongCTDT, pk=pk_chi_tiet_hp)
    ctdt = chi_tiet.chuong_trinh_dao_tao

    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể sửa chi tiết học phần cho CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:danh_sach_hoc_phan_theo_ctdt', pk_ctdt=ctdt.pk)

    if request.method == 'POST':
        form = ChiTietHocPhanTrongCTDTModelForm(request.POST, instance=chi_tiet)
        if form.is_valid():
            form.save()
            messages.success(request, f"Đã cập nhật chi tiết cho học phần: {chi_tiet.hoc_phan.ten_hoc_phan}")
            return redirect('daotao:danh_sach_hoc_phan_theo_ctdt', pk_ctdt=ctdt.pk)
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật. Vui lòng kiểm tra lại các trường.")
    else:
        form = ChiTietHocPhanTrongCTDTModelForm(instance=chi_tiet)

    context = {
        'form': form,
        'ctdt': ctdt,
        'chi_tiet': chi_tiet,
        'page_title': f'Cập nhật Chi tiết Học phần: {chi_tiet.hoc_phan.ten_hoc_phan}'
    }
    return render(request, 'daotao/sua_hoc_phan_ctdt.html', context)
@login_required
def xoa_chi_tiet_hp_trong_ctdt(request, pk_chi_tiet_hp):
    chi_tiet = get_object_or_404(ChiTietHocPhanTrongCTDT, pk=pk_chi_tiet_hp)
    ctdt = chi_tiet.chuong_trinh_dao_tao

    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể xóa học phần khỏi CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.pk)

    if request.method == 'POST':
        hoc_phan_ten = chi_tiet.hoc_phan.ten_hoc_phan
        chi_tiet.delete()
        messages.success(request, f"Đã xóa học phần '{hoc_phan_ten}' khỏi chương trình đào tạo.")
        return redirect(f"{reverse('daotao:chi_tiet_ctdt', kwargs={'pk_ctdt': ctdt.pk})}#hocphan-tab-pane")

    context = {
        'chi_tiet': chi_tiet,
        'ctdt': ctdt,
        'page_title': f'Xác nhận Xóa Học phần: {chi_tiet.hoc_phan.ten_hoc_phan}'
    }
    return render(request, 'daotao/xoa_chi_tiet_hp_trong_ctdt_confirm.html', context)

@login_required
def xoa_hoc_phan_ctdt(request, pk_chi_tiet_hp):
    chi_tiet = get_object_or_404(ChiTietHocPhanTrongCTDT, pk=pk_chi_tiet_hp)
    ctdt = chi_tiet.chuong_trinh_dao_tao

    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể xóa học phần khỏi CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:danh_sach_hoc_phan_theo_ctdt', pk_ctdt=ctdt.pk)

    if request.method == 'POST':
        hoc_phan_ten = chi_tiet.hoc_phan.ten_hoc_phan
        chi_tiet.delete()
        messages.success(request, f"Đã xóa học phần '{hoc_phan_ten}' khỏi chương trình đào tạo.")
        return redirect('daotao:danh_sach_hoc_phan_theo_ctdt', pk_ctdt=ctdt.pk)

    context = {
        'chi_tiet': chi_tiet,
        'ctdt': ctdt,
        'page_title': f'Xác nhận Xóa Học phần: {chi_tiet.hoc_phan.ten_hoc_phan}'
    }
    return render(request, 'daotao/xoa_hoc_phan_ctdt_confirm.html', context)
@login_required
@require_http_methods(["POST"])
def update_chi_tiet_hoc_phan_inline(request):
    return JsonResponse({'status': 'error', 'message': 'Chức năng chưa được triển khai.'})

@login_required
@require_http_methods(["POST"])
def update_muc_tieu_dao_tao_inline(request):
    pk = request.POST.get('pk')
    field = request.POST.get('field')
    value = request.POST.get('value')

    try:
        po = get_object_or_404(MucTieuDaoTao, pk=pk)
        
        # Security check: only allow updating specific fields
        allowed_fields = ['ma_muc_tieu', 'noi_dung']
        if field not in allowed_fields:
            return JsonResponse({'status': 'error', 'message': 'Trường không được phép chỉnh sửa.'})

        # Check if CTDT is in DRAFT status
        if po.chuong_trinh_dao_tao.trang_thai != 'DRAFT':
            return JsonResponse({'status': 'error', 'message': 'Chỉ có thể sửa khi CTĐT ở trạng thái "Bản nháp".'})

        setattr(po, field, value)
        po.save(update_fields=[field])
        
        return JsonResponse({'status': 'success', 'message': 'Cập nhật thành công!', 'new_value': value})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def danh_sach_don_vi(request):
    return HttpResponse(f"Chức năng danh sách đơn vị chưa được triển khai.")

@login_required
def them_don_vi(request):
    return HttpResponse(f"Chức năng thêm đơn vị chưa được triển khai.")

@login_required
def sua_don_vi(request, pk_don_vi):
    return HttpResponse(f"Chức năng sửa đơn vị {pk_don_vi} chưa được triển khai.")

@login_required
def xoa_don_vi(request, pk_don_vi):
    return HttpResponse(f"Chức năng xóa đơn vị {pk_don_vi} chưa được triển khai.")

@login_required
def them_chuan_dau_ra(request, pk_ctdt):
    ctdt = get_object_or_404(ChuongTrinhDaoTao, pk=pk_ctdt)
    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể thêm Chuẩn đầu ra cho CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=pk_ctdt)

    if request.method == 'POST':
        form = ChuanDauRaForm(request.POST)
        if form.is_valid():
            cdr = form.save(commit=False)
            cdr.chuong_trinh_dao_tao = ctdt
            cdr.save()
            form.save_m2m() # Needed for ManyToMany fields like 'dap_ung_muc_tieu'
            messages.success(request, "Đã thêm Chuẩn đầu ra thành công!")
            return redirect(f"{reverse('daotao:chi_tiet_ctdt', kwargs={'pk_ctdt': ctdt.pk})}#cdr-tab-pane")
        else:
            messages.error(request, "Có lỗi xảy ra khi thêm. Vui lòng kiểm tra lại các trường.")
    else:
        form = ChuanDauRaForm()
        # Filter the queryset for 'dap_ung_muc_tieu' to only show POs from the current CTDT
        form.fields['dap_ung_muc_tieu'].queryset = MucTieuDaoTao.objects.filter(chuong_trinh_dao_tao=ctdt)

    context = {
        'form': form,
        'ctdt': ctdt,
        'page_title': f'Thêm Chuẩn Đầu Ra cho CTĐT: {ctdt.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/them_chuan_dau_ra.html', context)

@login_required
def sua_chuan_dau_ra(request, pk_cdr):
    cdr = get_object_or_404(ChuanDauRa, pk=pk_cdr)
    ctdt = cdr.chuong_trinh_dao_tao

    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể sửa Chuẩn đầu ra cho CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.pk)

    if request.method == 'POST':
        form = ChuanDauRaForm(request.POST, instance=cdr)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật Chuẩn đầu ra thành công!")
            return redirect(f"{reverse('daotao:chi_tiet_ctdt', kwargs={'pk_ctdt': ctdt.pk})}#cdr-tab-pane")
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật. Vui lòng kiểm tra lại các trường.")
    else:
        form = ChuanDauRaForm(instance=cdr)
        form.fields['dap_ung_muc_tieu'].queryset = MucTieuDaoTao.objects.filter(chuong_trinh_dao_tao=ctdt)

    context = {
        'form': form,
        'ctdt': ctdt,
        'cdr': cdr,
        'page_title': f'Cập nhật Chuẩn Đầu Ra: {cdr.ma_cdr}'
    }
    return render(request, 'daotao/sua_chuan_dau_ra.html', context)

@login_required
def xoa_chuan_dau_ra(request, pk_cdr):
    return HttpResponse(f"Chức năng xóa chuẩn đầu ra {pk_cdr} chưa được triển khai.")

@login_required
def sua_muc_tieu_dao_tao(request, pk_po):
    muc_tieu = get_object_or_404(MucTieuDaoTao, pk=pk_po)
    ctdt = muc_tieu.chuong_trinh_dao_tao

    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể sửa Mục tiêu đào tạo cho CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.pk)

    if request.method == 'POST':
        form = MucTieuDaoTaoForm(request.POST, instance=muc_tieu)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật Mục tiêu đào tạo thành công!")
            return redirect(f"{reverse('daotao:chi_tiet_ctdt', kwargs={'pk_ctdt': ctdt.pk})}#po-tab-pane")
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật. Vui lòng kiểm tra lại các trường.")
    else:
        form = MucTieuDaoTaoForm(instance=muc_tieu)

    context = {
        'form': form,
        'ctdt': ctdt,
        'muc_tieu': muc_tieu,
        'page_title': f'Cập nhật Mục tiêu: {muc_tieu.ma_muc_tieu}'
    }
    return render(request, 'daotao/sua_muc_tieu_dao_tao.html', context)

@login_required
def xoa_muc_tieu_dao_tao(request, pk_po):
    muc_tieu = get_object_or_404(MucTieuDaoTao, pk=pk_po)
    ctdt = muc_tieu.chuong_trinh_dao_tao

    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể xóa Mục tiêu đào tạo cho CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.pk)

    if request.method == 'POST':
        muc_tieu.delete()
        messages.success(request, f"Đã xóa thành công Mục tiêu đào tạo: {muc_tieu.ma_muc_tieu}")
        return redirect(f"{reverse('daotao:chi_tiet_ctdt', kwargs={'pk_ctdt': ctdt.pk})}#po-tab-pane")

    context = {
        'object': muc_tieu,
        'ctdt': ctdt,
        'page_title': f'Xác nhận xóa Mục tiêu: {muc_tieu.ma_muc_tieu}'
    }
    return render(request, 'daotao/xoa_muc_tieu_dao_tao_confirm.html', context)

@login_required
def get_nganh_dao_tao_options(request):
    return JsonResponse([], safe=False)

@login_required
def get_don_vi_dao_tao_options(request):
    return JsonResponse([], safe=False)

# --- PLACEHOLDER FUNCTIONS END ---

#region Đơn vị Đào tạo
@login_required
def danh_sach_don_vi(request):
    query = request.GET.get('q', '')
    don_vi_list = DonViDaoTao.objects.all()
    if query:
        don_vi_list = don_vi_list.filter(
            Q(ma_don_vi__icontains=query) | Q(ten_don_vi__icontains=query)
        )
    context = {
        'don_vi_list': don_vi_list,
        'page_title': 'Quản lý Đơn vị Đào tạo',
        'query': query
    }
    return render(request, 'daotao/danh_sach_don_vi.html', context)

@login_required
def them_don_vi(request):
    if request.method == 'POST':
        form = DonViDaoTaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm đơn vị đào tạo thành công!')
            return redirect('daotao:danh_sach_don_vi')
        else:
            messages.error(request, 'Vui lòng sửa các lỗi bên dưới.')
    else:
        form = DonViDaoTaoForm()
    context = {
        'form': form,
        'page_title': 'Thêm Đơn vị Đào tạo'
    }
    return render(request, 'daotao/don_vi_form.html', context)

@login_required
def sua_don_vi(request, pk):
    don_vi = get_object_or_404(DonViDaoTao, pk=pk)
    if request.method == 'POST':
        form = DonViDaoTaoForm(request.POST, instance=don_vi)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật đơn vị đào tạo thành công!')
            return redirect('daotao:danh_sach_don_vi')
        else:
            messages.error(request, 'Vui lòng sửa các lỗi bên dưới.')
    else:
        form = DonViDaoTaoForm(instance=don_vi)
    context = {
        'form': form,
        'page_title': f'Sửa Đơn vị: {don_vi.ten_don_vi}'
    }
    return render(request, 'daotao/don_vi_form.html', context)

@login_required
def xoa_don_vi(request, pk):
    don_vi = get_object_or_404(DonViDaoTao, pk=pk)
    if request.method == 'POST':
        don_vi.delete()
        messages.success(request, 'Đã xóa đơn vị đào tạo thành công!')
        return redirect('daotao:danh_sach_don_vi')
    context = {
        'don_vi': don_vi,
        'page_title': f'Xác nhận xóa: {don_vi.ten_don_vi}'
    }
    return render(request, 'daotao/xoa_don_vi_confirm.html', context)
#endregion
