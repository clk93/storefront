# Generated by Django 4.1.5 on 2023-01-15 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_auto_20230115_1309'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='birthDate',
            new_name='birth_date',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='firstName',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='lastName',
            new_name='last_name',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='paymentStatus',
            new_name='payment_status',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='placedAt',
            new_name='placed_at',
        ),
        migrations.RenameField(
            model_name='orderitem',
            old_name='unitPrice',
            new_name='unit_price',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='number',
            new_name='inventory',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='updateDate',
            new_name='last_update',
        ),
    ]
