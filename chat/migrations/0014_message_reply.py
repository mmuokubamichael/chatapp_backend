# Generated by Django 4.0.4 on 2023-05-14 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0013_friendschat_restrict'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='reply',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chat.message'),
        ),
    ]