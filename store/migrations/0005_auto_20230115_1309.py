# Generated by Django 4.1.5 on 2023-01-15 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_add_zip_to_address'),
    ]

    operations = [
        migrations.RunSQL("""
        INSERT INTO store_collection (title)
        VALUES ('collection1')
        """, """
        DELETE FROM store_collection 
        WHERE title='collection1'
        """)
    ]
