from django.shortcuts import render, get_object_or_404, redirect
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

# Các view cơ bản cho CTĐT, Học Phần, Đơn Vị... (giữ nguyên)
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
            form_moi = ChuongTrinhDaoTaoModelForm()
            return render(request, 'daotao/them_ctdt.html', {
                'form': form_moi,
                'message': 'Đã thêm Chương trình Đào tạo thành công!'
            })
    else:
        form = ChuongTrinhDaoTaoModelForm()
    context = {
        'form': form,
        'page_title': 'Thêm Chương Trình Đào Tạo Mới'
    }
    return render(request, 'daotao/them_ctdt.html', context)

def danh_sach_ctdt(request):
    chuong_trinh_list = ChuongTrinhDaoTao.objects.all().order_by('-ngay_cap_nhat')
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
    context = {
        'ctdt': chuong_trinh,
        'page_title': f"Chi tiết CTĐT: {chuong_trinh.ten_nganh_ctdt}",
        'hoc_phan_trong_ctdt': hoc_phan_trong_ctdt,
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
        'hoc_phan_trong_ctdt': hoc_phan_trong_ctdt, # Add this to context
        'page_title': f'Cập nhật Chương trình: {ctdt.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/sua_ctdt.html', context)

def danh_sach_hoc_phan(request):
    hoc_phan_list = HocPhan.objects.all().order_by('ma_hoc_phan')
    paginator = Paginator(hoc_phan_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'page_title': 'Danh Sách Học Phần'
    }
    return render(request, 'daotao/danh_sach_hoc_phan.html', context)

# ===================================================================
# VIEW ĐƯỢC SỬA LỖI HOÀN TOÀN
# ===================================================================
@login_required
def them_hoc_phan_hang_loat(request, pk_ctdt):
    ctdt = get_object_or_404(ChuongTrinhDaoTao, pk=pk_ctdt)

    # Xử lý yêu cầu AJAX từ DataTables
    if request.method == 'GET' and request.GET.get('format') == 'datatables':
        try:
            draw = int(request.GET.get('draw', 1))
            start = int(request.GET.get('start', 0))
            length = int(request.GET.get('length', 10))
            
            search_ma_hp = request.GET.get('search_ma_hp', '')
            search_ten_hp = request.GET.get('search_ten_hp', '')

            # Truy vấn cơ sở đã được tối ưu
            queryset = HocPhan.objects.select_related('don_vi_quan_ly_goc').order_by('ma_hoc_phan')
            total_records = queryset.count()

            # Áp dụng bộ lọc
            if search_ma_hp:
                queryset = queryset.filter(ma_hoc_phan__icontains=search_ma_hp)
            if search_ten_hp:
                queryset = queryset.filter(ten_hoc_phan__icontains=search_ten_hp)

            filtered_records = queryset.count()

            # Phân trang
            paginated_queryset = queryset[start:start + length]

            # Lấy danh sách các học phần đã có trong CTĐT
            existing_hp_pks_set = set(ChiTietHocPhanTrongCTDT.objects.filter(
                chuong_trinh_dao_tao=ctdt
            ).values_list('hoc_phan__pk', flat=True))

            # Chuẩn bị dữ liệu trả về
            data = []
            for hp in paginated_queryset:
                try:
                    is_disabled = hp.pk in existing_hp_pks_set
                    checkbox_html = f'''
                        <input type="checkbox" name="selected_hoc_phan" value="{hp.pk}" class="hoc-phan-checkbox"
                        {'disabled' if is_disabled else ''} title="{'Học phần này đã có trong CTĐT' if is_disabled else ''}">
                    '''
                    don_vi_name = hp.don_vi_quan_ly_goc.ten_don_vi if hp.don_vi_quan_ly_goc else "N/A"
                    mo_ta_text = hp.mo_ta_hoc_phan or ""
                    mo_ta_display = mo_ta_text[:100] + '...' if len(mo_ta_text) > 100 else mo_ta_text

                    data.append([
                        checkbox_html,
                        hp.ma_hoc_phan,
                        hp.ten_hoc_phan,
                        hp.tong_so_tin_chi_goc,
                        don_vi_name,
                        mo_ta_display
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
            # Trả về lỗi nếu có sự cố
            return JsonResponse({"error": str(e), "data": [], "recordsFiltered": 0, "recordsTotal": 0}, status=500)

    # Xử lý yêu cầu POST để thêm học phần
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
                if hoc_ky_du_kien_default is not None:
                    chi_tiet_hp_data['hoc_ky_du_kien'] = hoc_ky_du_kien_default
                if la_bat_buoc_default is not None:
                    chi_tiet_hp_data['la_bat_buoc'] = la_bat_buoc_default

                form_instance = ChiTietHocPhanTrongCTDTModelForm(data=chi_tiet_hp_data)
                if form_instance.is_valid():
                    form_instance.save()
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
        
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.pk)

    # Xử lý yêu cầu GET ban đầu để tải trang
    context = {
        'ctdt': ctdt,
        'page_title': f'Thêm Học Phần Hàng Loạt cho CTĐT: {ctdt.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/them_hoc_phan_hang_loat.html', context)

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

@login_required
def gui_duyet_ctdt(request, pk_ctdt):
    # Placeholder
    return HttpResponse(f"Chức năng gửi duyệt cho CTĐT {pk_ctdt} chưa được triển khai.")

@login_required
def xu_ly_duyet_ctdt(request, pk_ctdt, action):
    # Placeholder
    return HttpResponse(f"Chức năng xử lý duyệt ({action}) cho CTĐT {pk_ctdt} chưa được triển khai.")

@login_required
def tao_phien_ban_moi_ctdt(request, pk_ctdt):
    # Placeholder
    return HttpResponse(f"Chức năng tạo phiên bản mới cho CTĐT {pk_ctdt} chưa được triển khai.")

@login_required
def luu_tru_ctdt(request, pk_ctdt):
    # Placeholder
    return HttpResponse(f"Chức năng lưu trữ CTĐT {pk_ctdt} chưa được triển khai.")

@login_required
def upload_hoc_phan_ctdt(request, pk_ctdt):
    # Placeholder
    return HttpResponse(f"Chức năng upload học phần cho CTĐT {pk_ctdt} chưa được triển khai.")

@login_required
def download_hoc_phan_ctdt_template(request):
    # Placeholder
    return HttpResponse("Chức năng download template chưa được triển khai.")

def them_hoc_phan_vao_ctdt(request):
    # Placeholder
    return HttpResponse("Chức năng thêm học phần vào CTĐT chưa được triển khai.")

@login_required
def danh_sach_hoc_phan_theo_ctdt(request, pk_ctdt):
    ctdt = get_object_or_404(ChuongTrinhDaoTao, pk=pk_ctdt)
    hoc_phan_trong_ctdt = ChiTietHocPhanTrongCTDT.objects.filter(
        chuong_trinh_dao_tao=ctdt
    ).order_by('hoc_ky_du_kien', 'hoc_phan__ma_hoc_phan')

    context = {
        'ctdt': ctdt,
        'hoc_phan_trong_ctdt': hoc_phan_trong_ctdt,
        'page_title': f'Danh sách Học phần trong CTĐT: {ctdt.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/danh_sach_hoc_phan_theo_ctdt.html', context)

def chi_tiet_hoc_phan_trong_ctdt(request, pk_chi_tiet_hp):
    # Placeholder
    return HttpResponse(f"Chi tiết học phần trong CTĐT {pk_chi_tiet_hp} chưa được triển khai.")

def sua_chi_tiet_hp_trong_ctdt(request, pk_chi_tiet_hp):
    # Placeholder
    return HttpResponse(f"Sửa chi tiết học phần trong CTĐT {pk_chi_tiet_hp} chưa được triển khai.")

@login_required
def xoa_chi_tiet_hp_trong_ctdt(request, pk_chi_tiet_hp):
    chi_tiet_hp = get_object_or_404(ChiTietHocPhanTrongCTDT, pk=pk_chi_tiet_hp)
    ctdt = chi_tiet_hp.chuong_trinh_dao_tao
    
    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể xóa học phần trong CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.id)

    if request.method == 'POST':
        chi_tiet_hp.delete()
        messages.success(request, f"Đã xóa học phần '{chi_tiet_hp.hoc_phan.ten_hoc_phan}' khỏi CTĐT '{ctdt.ten_nganh_ctdt}' thành công.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.id)
    
    context = {
        'chi_tiet_hp': chi_tiet_hp,
        'ctdt': ctdt,
        'page_title': f'Xác nhận Xóa Học phần: {chi_tiet_hp.hoc_phan.ten_hoc_phan}'
    }
    return render(request, 'daotao/xoa_chi_tiet_hp_trong_ctdt_confirm.html', context)

@login_required
def sua_hoc_phan(request, pk_hoc_phan):
    hoc_phan = get_object_or_404(HocPhan, pk=pk_hoc_phan)
    if request.method == 'POST':
        form = HocPhanLibModelForm(request.POST, instance=hoc_phan)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật Học phần thành công!")
            return redirect('daotao:danh_sach_hoc_phan')
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật Học phần. Vui lòng kiểm tra lại các trường.")
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
def danh_sach_don_vi(request):
    don_vi_list = DonViDaoTao.objects.all().order_by('ma_don_vi')
    paginator = Paginator(don_vi_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'page_title': 'Danh Sách Đơn Vị Đào Tạo'
    }
    return render(request, 'daotao/danh_sach_don_vi.html', context)

@login_required
def them_don_vi(request):
    if request.method == 'POST':
        form = DonViDaoTaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã thêm Đơn vị đào tạo thành công!")
            return redirect('daotao:danh_sach_don_vi')
        else:
            messages.error(request, "Có lỗi xảy ra khi thêm Đơn vị đào tạo. Vui lòng kiểm tra lại các trường.")
    else:
        form = DonViDaoTaoForm()
    context = {
        'form': form,
        'page_title': 'Thêm Đơn Vị Đào Tạo Mới'
    }
    return render(request, 'daotao/them_don_vi.html', context)

@login_required
def sua_don_vi(request, pk_don_vi):
    don_vi = get_object_or_404(DonViDaoTao, pk=pk_don_vi)
    if request.method == 'POST':
        form = DonViDaoTaoForm(request.POST, instance=don_vi)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật Đơn vị đào tạo thành công!")
            return redirect('daotao:danh_sach_don_vi')
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật Đơn vị đào tạo. Vui lòng kiểm tra lại các trường.")
    else:
        form = DonViDaoTaoForm(instance=don_vi)
    
    context = {
        'form': form,
        'don_vi': don_vi,
        'page_title': f'Cập nhật Đơn vị: {don_vi.ten_don_vi}'
    }
    return render(request, 'daotao/sua_don_vi.html', context)

@login_required
def xoa_don_vi(request, pk_don_vi):
    don_vi_can_xoa = get_object_or_404(DonViDaoTao, pk=pk_don_vi)
    if request.method == 'POST':
        don_vi_can_xoa.delete()
        messages.success(request, f"Đã xóa đơn vị đào tạo '{don_vi_can_xoa.ten_don_vi}' thành công.")
        return redirect('daotao:danh_sach_don_vi')
    context = {
        'don_vi': don_vi_can_xoa,
        'page_title': f'Xác nhận Xóa Đơn vị: {don_vi_can_xoa.ten_don_vi}'
    }
    return render(request, 'daotao/xoa_don_vi_confirm.html', context)

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
            form.save_m2m() # Save ManyToManyField for dap_ung_muc_tieu
            messages.success(request, "Đã thêm Chuẩn đầu ra thành công!")
            return redirect('daotao:sua_ctdt', pk_ctdt=ctdt.id) # Redirect back to edit CTDT page
        else:
            messages.error(request, "Có lỗi xảy ra khi thêm Chuẩn đầu ra. Vui lòng kiểm tra lại các trường.")
    else:
        form = ChuanDauRaForm()

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
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.id)

    if request.method == 'POST':
        form = ChuanDauRaForm(request.POST, instance=cdr)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật Chuẩn đầu ra thành công!")
            return redirect('daotao:sua_ctdt', pk_ctdt=ctdt.id)
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật Chuẩn đầu ra. Vui lòng kiểm tra lại các trường.")
    else:
        form = ChuanDauRaForm(instance=cdr)

    context = {
        'form': form,
        'cdr': cdr,
        'ctdt': ctdt,
        'page_title': f'Sửa Chuẩn Đầu Ra: {cdr.ma_cdr} của {ctdt.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/sua_chuan_dau_ra.html', context)

@login_required
def xoa_chuan_dau_ra(request, pk_cdr):
    cdr = get_object_or_404(ChuanDauRa, pk=pk_cdr)
    ctdt = cdr.chuong_trinh_dao_tao
    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể xóa Chuẩn đầu ra cho CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.id)

    if request.method == 'POST':
        cdr.delete()
        messages.success(request, f"Đã xóa Chuẩn đầu ra '{cdr.ma_cdr}' thành công.")
        return redirect('daotao:sua_ctdt', pk_ctdt=ctdt.id)
    
    context = {
        'cdr': cdr,
        'ctdt': ctdt,
        'page_title': f'Xác nhận Xóa Chuẩn Đầu Ra: {cdr.ma_cdr}'
    }
    return render(request, 'daotao/xoa_chuan_dau_ra_confirm.html', context)

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
            return redirect('daotao:sua_ctdt', pk_ctdt=ctdt.id)
        else:
            messages.error(request, "Có lỗi xảy ra khi thêm Mục tiêu đào tạo. Vui lòng kiểm tra lại các trường.")
    else:
        form = MucTieuDaoTaoForm()

    context = {
        'form': form,
        'ctdt': ctdt,
        'page_title': f'Thêm Mục tiêu đào tạo cho CTĐT: {ctdt.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/them_muc_tieu_dao_tao.html', context)

@login_required
def sua_muc_tieu_dao_tao(request, pk_po):
    mt = get_object_or_404(MucTieuDaoTao, pk=pk_po)
    ctdt = mt.chuong_trinh_dao_tao
    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể sửa Mục tiêu đào tạo cho CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.id)

    if request.method == 'POST':
        form = MucTieuDaoTaoForm(request.POST, instance=mt)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật Mục tiêu đào tạo thành công!")
            return redirect('daotao:sua_ctdt', pk_ctdt=ctdt.id)
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật Mục tiêu đào tạo. Vui lòng kiểm tra lại các trường.")
    else:
        form = MucTieuDaoTaoForm(instance=mt)

    context = {
        'form': form,
        'mt': mt,
        'ctdt': ctdt,
        'page_title': f'Sửa Mục tiêu đào tạo: {mt.ma_mt} của {ctdt.ten_nganh_ctdt}'
    }
    return render(request, 'daotao/sua_muc_tieu_dao_tao.html', context)

@login_required
def xoa_muc_tieu_dao_tao(request, pk_po):
    mt = get_object_or_404(MucTieuDaoTao, pk=pk_po)
    ctdt = mt.chuong_trinh_dao_tao
    if ctdt.trang_thai != 'DRAFT':
        messages.error(request, "Chỉ có thể xóa Mục tiêu đào tạo cho CTĐT ở trạng thái 'Bản nháp'.")
        return redirect('daotao:chi_tiet_ctdt', pk_ctdt=ctdt.id)

    if request.method == 'POST':
        mt.delete()
        messages.success(request, f"Đã xóa Mục tiêu đào tạo '{mt.ma_mt}' thành công.")
        return redirect('daotao:sua_ctdt', pk_ctdt=ctdt.id)
    
    context = {
        'mt': mt,
        'ctdt': ctdt,
        'page_title': f'Xác nhận Xóa Mục tiêu đào tạo: {mt.ma_mt}'
    }
    return render(request, 'daotao/xoa_muc_tieu_dao_tao_confirm.html', context)
