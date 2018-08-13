# Generated by Django 2.0.4 on 2018-08-13 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hellouser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='shipping_address2',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Дополнительный Адрес отправки'),
        ),
        migrations.AddField(
            model_name='myuser',
            name='shipping_city',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Город отправки'),
        ),
        migrations.AddField(
            model_name='myuser',
            name='shipping_country',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Страна отправки'),
        ),
        migrations.AddField(
            model_name='myuser',
            name='shipping_zip',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Почтовый индекс отправки'),
        ),
    ]
