# Generated by Django 2.0.4 on 2018-09-11 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hellouser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='waybillfreightpacking',
            name='barcode',
            field=models.CharField(default=0, max_length=32, verbose_name='ШтрихКод'),
        ),
        migrations.AddField(
            model_name='waybillfreightpacking',
            name='freight_packing',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='hellouser.FreightPackingType', verbose_name='Транспортная упаковка'),
        ),
        migrations.AddField(
            model_name='waybillfreightpacking',
            name='height',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=15, verbose_name='Высота ТУ'),
        ),
        migrations.AddField(
            model_name='waybillfreightpacking',
            name='length',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=15, verbose_name='Длина ТУ'),
        ),
        migrations.AddField(
            model_name='waybillfreightpacking',
            name='verified',
            field=models.BooleanField(default=True, verbose_name='Груз проверен'),
        ),
        migrations.AddField(
            model_name='waybillfreightpacking',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=15, verbose_name='Вес ТУ'),
        ),
        migrations.AddField(
            model_name='waybillfreightpacking',
            name='width',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=15, verbose_name='Ширина ТУ'),
        ),
    ]
