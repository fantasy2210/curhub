# Generated by Django 5.2.1 on 2025-07-14 03:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("daotao", "0008_alter_matrancdr_cthp_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="chuongtrinhdaotao",
            name="ly_do_thay_doi",
            field=models.TextField(
                blank=True, null=True, verbose_name="Lý do thay đổi phiên bản"
            ),
        ),
        migrations.AddField(
            model_name="chuongtrinhdaotao",
            name="phien_ban_goc",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="cac_phien_ban_sau",
                to="daotao.chuongtrinhdaotao",
                verbose_name="Thuộc phiên bản gốc",
            ),
        ),
        migrations.AddField(
            model_name="chuongtrinhdaotao",
            name="trang_thai",
            field=models.CharField(
                choices=[
                    ("DRAFT", "Bản nháp"),
                    ("PENDING_APPROVAL", "Chờ duyệt"),
                    ("APPROVED", "Đã phê duyệt"),
                    ("REJECTED", "Bị từ chối"),
                    ("ARCHIVED", "Lưu trữ"),
                ],
                default="DRAFT",
                max_length=20,
                verbose_name="Trạng thái",
            ),
        ),
        migrations.AddField(
            model_name="chuongtrinhdaotao",
            name="version",
            field=models.CharField(
                default="1.0", max_length=20, verbose_name="Phiên bản"
            ),
        ),
        migrations.CreateModel(
            name="LichSuThayDoiCTDT",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "thoi_gian",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Thời gian thay đổi"
                    ),
                ),
                (
                    "hanh_dong",
                    models.CharField(max_length=255, verbose_name="Hành động"),
                ),
                (
                    "chi_tiet_thay_doi",
                    models.TextField(
                        blank=True, null=True, verbose_name="Chi tiết thay đổi"
                    ),
                ),
                (
                    "chuong_trinh_dao_tao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lich_su_thay_doi",
                        to="daotao.chuongtrinhdaotao",
                        verbose_name="Chương trình đào tạo",
                    ),
                ),
                (
                    "nguoi_thuc_hien",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Người thực hiện",
                    ),
                ),
            ],
            options={
                "verbose_name": "Lịch sử thay đổi CTĐT",
                "verbose_name_plural": "Lịch sử thay đổi CTĐT",
                "ordering": ["-thoi_gian"],
            },
        ),
    ]
