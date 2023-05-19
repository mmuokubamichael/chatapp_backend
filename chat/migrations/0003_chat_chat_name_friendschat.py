# Generated by Django 4.0.4 on 2023-03-24 06:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_remove_message_author_contact_chat_message_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='chat_name',
            field=models.CharField(default='UNKNOWN', max_length=200),
        ),
        migrations.CreateModel(
            name='FriendsChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False)),
                ('messages', models.ManyToManyField(blank=True, to='chat.message')),
                ('reciever', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.contact')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_friends', to='chat.contact')),
            ],
        ),
    ]
