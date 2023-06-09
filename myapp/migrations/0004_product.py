# Generated by Django 4.1.7 on 2023-02-21 23:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_user_usertype_alter_user_profile_pic'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_category', models.CharField(choices=[('men', 'men'), ('women', 'women'), ('kid', 'kid')], max_length=100)),
                ('product_name', models.CharField(max_length=100)),
                ('product_price', models.PositiveIntegerField()),
                ('product_desc', models.TextField()),
                ('product_size', models.CharField(choices=[('s', 's'), ('m', 'm'), ('l', 'l'), ('xl', 'xl'), ('xxl', 'xxl')], max_length=100)),
                ('profile_image', models.ImageField(upload_to='product_pic/')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.user')),
            ],
        ),
    ]
