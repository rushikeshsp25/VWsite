# Generated by Django 2.2.6 on 2019-11-09 12:48

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(max_length=70, unique=True)),
                ('is_online', models.BooleanField(default=False)),
                ('level', models.CharField(choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')], max_length=20)),
                ('course_icon', models.FileField(upload_to='')),
                ('fees', models.IntegerField(default=0)),
                ('outcomes', models.TextField()),
                ('prerequisits', models.TextField()),
                ('description', models.TextField()),
                ('syllabus', models.FileField(upload_to='')),
                ('date_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('name', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=10)),
                ('year', models.CharField(choices=[('FE', 'First Year'), ('SE', 'Second Year'), ('TE', 'Third Year'), ('BE', 'Fourth Year'), ('NA', 'Not Applicable')], max_length=20)),
                ('college', models.ForeignKey(on_delete=models.SET('OTHER'), to='home.College')),
            ],
        ),
        migrations.CreateModel(
            name='StudentContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=10)),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='StudyCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('course_name', models.CharField(max_length=30)),
                ('material_file', models.FileField(upload_to='StudyCourse')),
            ],
        ),
        migrations.CreateModel(
            name='StudentCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('admission', models.BooleanField(default=False)),
                ('fees_paid', models.IntegerField(default=0)),
                ('comments', models.TextField()),
                ('rating', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], max_length=20)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Course', to_field='course_name')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Student')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('rating', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], max_length=20)),
                ('review', models.TextField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Course', to_field='course_name')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Student')),
            ],
        ),
    ]
