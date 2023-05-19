from django.contrib import admin
from .models import Message,Chat,Contact,FriendsChat,OnlineforChannels,Onlineforfriend

# Register your models here.

admin.site.register([Message,Chat,Contact,FriendsChat,OnlineforChannels,Onlineforfriend])
