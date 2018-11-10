# Generated by Django 2.1.3 on 2018-11-10 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('field_type', models.CharField(choices=[('text', 'Text'), ('number', 'Number'), ('date', 'Date'), ('enum', 'Enum')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='FieldValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_text', models.TextField(blank=True, null=True)),
                ('value_number', models.IntegerField(blank=True, null=True)),
                ('value_date', models.DateField(blank=True, null=True)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_values', to='core.Field')),
            ],
        ),
        migrations.CreateModel(
            name='OptionValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Risk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='RiskType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='risk',
            name='risk_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='risks', to='core.RiskType'),
        ),
        migrations.AddField(
            model_name='fieldvalue',
            name='risk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_values', to='core.Risk'),
        ),
        migrations.AddField(
            model_name='fieldvalue',
            name='value_option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='field_values', to='core.OptionValue'),
        ),
        migrations.AddField(
            model_name='field',
            name='options',
            field=models.ManyToManyField(blank=True, to='core.OptionValue'),
        ),
        migrations.AddField(
            model_name='field',
            name='risk_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='core.RiskType'),
        ),
    ]
