# Generated by Django 3.1.7 on 2021-05-30 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LoVisto', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('date', models.DateField()),
                ('user', models.CharField(max_length=512)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LoVisto.content')),
            ],
        ),
    ]