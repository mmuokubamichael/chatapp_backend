from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.conf import settings

# Create your models here.

def generate_unique_id():
    random_uuid = uuid.uuid4()
    unique_id = str(random_uuid.int)[:4]
    return unique_id

class Contact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, blank=True)
    friends = models.ManyToManyField('self',blank=True)
    slug= models.CharField(max_length=100, blank=True)
    online = models.DateTimeField(auto_now=True)
    image= models.ImageField(upload_to="user/image_profile/",blank=True)

    def save(self,*args,**kwargs):
        if self.slug == None:
            self.slug = "f"+str(self.user.username)+generate_unique_id
        return super().save(*args,**kwargs)

    def __str__(self):
        return str(self.user.username)

class Message(models.Model):
    contact = models.ForeignKey(Contact, related_name="messages",on_delete=models.CASCADE, blank=True)
    reply = models.ForeignKey('self',on_delete=models.SET_NULL, blank=True,null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.contact.user.username)
    
class Chat(models.Model):
    participants = models.ManyToManyField(Contact, related_name="chats" , blank=True)
    admin = models.ManyToManyField(Contact, related_name="admins" , blank=True)
    restrict = models.ManyToManyField(Contact, related_name="restrictions" , blank=True)
    messages = models.ManyToManyField(Message,blank=True)
    chat_name = models.CharField(max_length=200)
    chat_slug = models.CharField(max_length=300,blank=True)
    image= models.ImageField(upload_to="channel/image_profile/",blank=True)

    def __str__(self):
        return str(self.chat_name)
    


class FriendsChat(models.Model):
    sender =  models.ForeignKey(Contact, on_delete=models.CASCADE,related_name="my_friends")
    messages = models.ManyToManyField(Message,blank=True)
    reciever = models.ForeignKey(Contact, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    slug = models.CharField(max_length=200,blank=True)
    restrict = models.ManyToManyField(Contact, related_name="restrictFriend" , blank=True)
    

class OnlineforChannels(models.Model):
    group = models.ForeignKey(Chat,on_delete=models.CASCADE)
    participant = models.ForeignKey(Contact,on_delete=models.CASCADE)
    online = models.DateTimeField(auto_now=True)

class Onlineforfriend(models.Model):
    friendchat = models.ForeignKey(FriendsChat,on_delete=models.CASCADE)
    participant = models.ForeignKey(Contact,on_delete=models.CASCADE)
    online = models.DateTimeField(auto_now=True)