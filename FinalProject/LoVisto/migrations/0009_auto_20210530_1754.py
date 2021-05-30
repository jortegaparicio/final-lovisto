# Generated by Django 3.1.7 on 2021-05-30 17:54

import LoVisto.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LoVisto', '0008_auto_20210530_1738'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(default='', max_length=128)),
                ('password', models.CharField(default='', max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='content',
            name='user_name',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='content',
            name='link',
            field=models.CharField(default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='content',
            name='title',
            field=models.CharField(default='', max_length=512),
        ),
        migrations.AlterField(
            model_name='content',
            name='user',
            field=models.ForeignKey(default=LoVisto.models.User, on_delete=django.db.models.deletion.CASCADE, to='LoVisto.user'),
        ),
    ]
