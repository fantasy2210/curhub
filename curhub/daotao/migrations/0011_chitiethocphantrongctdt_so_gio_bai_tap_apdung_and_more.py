# Generated by Django 5.2.1 on 2025-07-23 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("daotao", "0010_chuongtrinhdaotao_ghi_chu_ctdt_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="chitiethocphantrongctdt",
            name="so_gio_bai_tap_apdung",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Số giờ Bài tập áp dụng"
            ),
        ),
        migrations.AddField(
            model_name="chitiethocphantrongctdt",
            name="so_gio_bai_tap_lon_apdung",
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                null=True,
                verbose_name="Số giờ Bài tập lớn áp dụng",
            ),
        ),
        migrations.AddField(
            model_name="chitiethocphantrongctdt",
            name="so_gio_do_an_apdung",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Số giờ Đồ án áp dụng"
            ),
        ),
        migrations.AddField(
            model_name="chitiethocphantrongctdt",
            name="so_gio_lms_apdung",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Số giờ LMS áp dụng"
            ),
        ),
        migrations.AddField(
            model_name="chitiethocphantrongctdt",
            name="so_gio_luan_an_apdung",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Số giờ Luận án áp dụng"
            ),
        ),
        migrations.AddField(
            model_name="chitiethocphantrongctdt",
            name="so_gio_thuc_tap_apdung",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Số giờ Thực tập áp dụng"
            ),
        ),
        migrations.AddField(
            model_name="hocphan",
            name="edusoft_id",
            field=models.BigIntegerField(
                blank=True, null=True, unique=True, verbose_name="ID từ Edusoft (IDMH)"
            ),
        ),
        migrations.AddField(
            model_name="hocphan",
            name="so_gio_bai_tap_goc",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Số giờ Bài tập gốc (BT)"
            ),
        ),
        migrations.AddField(
            model_name="hocphan",
            name="so_gio_bai_tap_lon_goc",
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                null=True,
                verbose_name="Số giờ Bài tập lớn gốc (BTL)",
            ),
        ),
        migrations.AddField(
            model_name="hocphan",
            name="so_gio_do_an_goc",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Số giờ Đồ án gốc (DA)"
            ),
        ),
        migrations.AddField(
            model_name="hocphan",
            name="so_gio_lms_goc",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Số giờ LMS gốc (LMS)"
            ),
        ),
        migrations.AddField(
            model_name="hocphan",
            name="so_gio_luan_an_goc",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Số giờ Luận án gốc (LA)"
            ),
        ),
        migrations.AddField(
            model_name="hocphan",
            name="so_gio_thuc_tap_goc",
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                null=True,
                verbose_name="Số giờ Thực tập gốc (TT)",
            ),
        ),
    ]
