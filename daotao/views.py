from django.shortcuts import render, redirect
from .forms import ChuongTrinhDaoTaoModelForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def them_chuong_trinh_dao_tao(request):
    if request.method == 'POST':
        form = ChuongTrinhDaoTaoModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới chương trình đào tạo thành công!')
            return redirect('daotao:danh_sach_ctdt')
    else:
        form = ChuongTrinhDaoTaoModelForm()

    context = {
        'form': form,
        'page_title': 'Thêm Mới Chương Trình Đào Tạo'
    }
    return render(request, 'daotao/them_ctdt.html', context)