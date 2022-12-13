# Generated by Django 4.0.6 on 2022-11-06 02:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cMenu', '0003_alter_menuitems_argument_alter_menuitems_bottomline_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='menuGroups',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('GroupName', models.CharField(max_length=100, unique=True)),
                ('GroupInfo', models.CharField(blank=True, max_length=250)),
            ],
        ),
        migrations.AlterModelOptions(
            name='menuitems',
            options={'ordering': ['MenuGroup', 'MenuID', 'OptionNumber']},
        ),
        migrations.AddField(
            model_name='menuitems',
            name='MenuGroup',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='cMenu.menugroups'),
        ),
    ]