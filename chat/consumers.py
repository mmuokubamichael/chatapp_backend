import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message
from django.contrib.auth import get_user_model
from chat.models import Chat,Message,Contact,FriendsChat
from django.shortcuts import get_object_or_404
from django.db.models import Q


class ChatConsumer(WebsocketConsumer):
    user = get_user_model()

    def fetch_message(self,data):
        print(data["chaturl"])
        cat = data["chaturl"][0]
        if cat == "f":
            #handle friends part
            friend_name = data["chaturl"][1:]
            
            user_contact = Contact.objects.get(user__username=data["username"])
            friend_contact = Contact.objects.filter(user__username=friend_name)
            
            if friend_contact.exists():
                print("aceepted")
                if friend_contact[0] in user_contact.friends.all():
                    #get friend and user chat
                    print("aceepted")
                    friend_chat= FriendsChat.objects.filter(Q(sender=user_contact,reciever=friend_contact[0])|Q(sender=friend_contact[0],reciever=user_contact))
                    print("aceepted")
                    print(friend_chat)
                    if friend_chat[0].accepted:
                        #accepted
                        
                       
                        
                        content = {
                            "comand":"fetch_messsage",
                            "accepted":"yes",
                            "cat":"f",
                            "objectexist":True,
                            "navigate":friend_chat[0].slug,
                            "messages": [],
                            "userFriend": friend_contact[0].user.username,
                            "navpic":friend_contact[0].image.url if friend_contact[0].image else None
                        }
                        self.send_message(content)
                    else:
                        #not accepted
                        
                        content = {
                            "comand":"fetch_messsage",
                            "accepted":"no",
                            "sender": friend_chat[0].sender.user.username,
                            "reciever":friend_chat[0].reciever.user.username,
                            "cat":"f",
                            "objectexist":True,
                            "messages": [],
                            "userFriend": friend_contact[0].user.username,
                            "navpic":friend_contact[0].image.url if friend_contact[0].image else None
                        }
                
                        self.send_message(content)
                else:
                    #if user not your friend
                    content = {
                            "comand":"fetch_messsage",
                            
                            "is_not_friend": True,
                            "friend":friend_contact[0].user.username,
                            "cat":"f",
                            "objectexist":True,
                            "messages": [],
                            "userFriend": friend_contact[0].user.username,
                            "navpic":friend_contact[0].image.url if friend_contact[0].image else None
                        }
                
                    self.send_message(content)
                    print("user not your friend")
                    

            else:
                # return user does not exist
                content = {
                            "comand":"fetch_messsage",
                            "user_not_exists":True,
                            "cat":"f",
                            "objectexist":False,
                            "messages": []
                        }
                
                self.send_message(content)
                print("user does not exist")



        elif cat == "_":
            user_contact = Contact.objects.get(user__username=data["username"])
            friend_chat= FriendsChat.objects.filter(Q(sender=user_contact,slug=data["chaturl"],accepted=True)|Q(slug=data["chaturl"],reciever=user_contact,accepted=True))
            if friend_chat[0].sender.user.username == user_contact.user.username:
                user_friend = friend_chat[0].reciever.user.username
                navpic = friend_chat[0].reciever.image.url if friend_chat[0].reciever.image else None
                
            else:
                user_friend = friend_chat[0].sender.user.username
                navpic = friend_chat[0].sender.image.url if friend_chat[0].sender.image  else None
            if friend_chat.exists():
                msgs = friend_chat[0].messages.all()
                content = {
                    "comand":"fetch_messsage",
                    "notfriendChat":False,
                    "objectexist":True,
                    "cat":"_",
                    "messages": self.convert_messages_json(msgs),
                    "userFriend":user_friend,
                    "navpic":navpic,
                    "restrict_user": self.convert_restricted_user(friend_chat[0].restrict.all()) if friend_chat[0].restrict.all().exists() else [],
                }
                self.send_message(content)
            else:
                content = {
                    "comand":"fetch_messsage",
                    "notfriendChat":True,
                    "objectexist":False,
                    "cat":"_",
                    "messages": []
                }
                self.send_message(content)
        else:
            # handle channel part
             #get_chat = get_object_or_404(Chat,chat_slug=data["chaturl"])
            user_contact = Contact.objects.get(user__username=data["username"])
            get_userchat = Chat.objects.filter(chat_slug=data["chaturl"])
            if get_userchat.exists():
                if user_contact in get_userchat[0].participants.all():
                    msgs = get_userchat[0].messages.all()
                    pts = get_userchat[0].participants.all()
                    admin = get_userchat[0].admin.all()
                    restrict_user = get_userchat[0].restrict.all()
                    pts_count = get_userchat[0].participants.all().count()
                    content = {
                        "comand":"fetch_messsage",
                        "exists":"yes",
                        "objectexist":True,
                        "cat":"c",
                        "navpic": get_userchat[0].image.url if get_userchat[0].image else None,
                        "chat_name":get_userchat[0].chat_name,
                        "messages": self.convert_messages_json(msgs),
                        'participants':self.convert_participant_json(pts),
                        'admins':self.convert_participant_json(admin),
                        "restrict_user":self.convert_restricted_user(restrict_user) if get_userchat[0].restrict.all().exists() else [],
                        "participants_count": pts_count

                    }
                    self.send_message(content)
                else:
                    msgs = get_userchat[0].messages.all()
                    pts = get_userchat[0].participants.all()
                    admin = get_userchat[0].admin.all()
                    restrict_user = get_userchat[0].restrict.all()
                    pts_count = get_userchat[0].participants.all().count()
                    content = {
                    "comand":"fetch_messsage",
                    "exists":"not_participant",
                    "objectexist":True,
                    "chat_name":get_userchat[0].chat_name,
                    "cat":"c",
                    "navpic":get_userchat[0].image.url if get_userchat[0].image else None,
                    "messages": self.convert_messages_json(msgs),
                    'participants':self.convert_participant_json(pts),
                    'admins':self.convert_participant_json(admin),
                    "restrict_user": self.convert_restricted_user(restrict_user) if get_userchat[0].restrict.all().exists() else [],
                    "participants_count": pts_count
                    }
                    self.send_message(content)
                
            else:
                content = {
                "comand":"fetch_messsage",
                "exists":"no",
                "objectexist":False,
                "cat":"c",
                "chaterror":True,
                "messages": [],
                "participants":[]
                }
                self.send_message(content)
           
    def convert_restricted_user(self,contacts):
        users = []
        for ct in contacts:
            users.append(ct.user.username)
        return users    
       
        
    def convert_participant_json(self,contacts):
        users = []
        for ct in contacts:
            users.append(self.participant_json(ct))
        return users
    
    def participant_json(self,cts):
        return {
            "id":cts.id,
            "author": cts.user.username,
            "image":cts.image.url if cts.image else None,
            
        }     

    def convert_messages_json(self,massage):
        msg = []
        for ms in massage:
            msg.append(self.messages_json(ms))
        return msg
    
    def messages_json(self,mess):
        return {
            "id":mess.id,
            "author": mess.contact.user.username,
            "content":mess.content,
            "timestamp":str(mess.timestamp),
            "prof_image":mess.contact.image.url if mess.contact.image else None,
            "repliedChatUser":mess.reply.contact.user.username if mess.reply else None,
            "repliedChat":mess.reply.content if mess.reply else None,
        }

    def send_chat_message(self,data):
        user = get_user_model()
        if data["chaturl"][0] == "_":
            print(data["chaturl"])
            author_name = data["from"]
            user_model = user.objects.filter(username=author_name)[0]
            # getting contact
            user_contact , created = Contact.objects.get_or_create(user=user_model)
            #friendcontact = Contact.objects.get(user__username=data["chaturl"][1:])
            
            
            
            #get_chat = get_object_or_404(Chat,)
            friend_chat= FriendsChat.objects.filter(Q(sender=user_contact,slug=data["chaturl"])|Q(slug=data["chaturl"],reciever=user_contact))
            if friend_chat[0].restrict.all().exists():
                if user_contact == friend_chat[0].sender:
                    if friend_chat[0].reciever in friend_chat[0].restrict.all():            
                        content= {
                            "comand":"chat_message",
                            "restrict_message": "Unblock user to send a message",
                            "is_user_restricted":True,
                            "message":[]
                        }
                        return self.send_message_to_group(content)
                    else:
                        content= {
                            "comand":"chat_message",
                            "restrict_message": "you have been Blocked from sending message",
                            "is_user_restricted":True,
                            "message":[]
                        }
                        return self.send_message_to_group(content)
                else:
                    if friend_chat[0].sender in friend_chat[0].restrict.all():            
                        content= {
                            "comand":"chat_message",
                            "restrict_message": "Unblock user to send a message",
                            "is_user_restricted":True,
                            "message":[]
                        }
                        return self.send_message_to_group(content)
                    else:
                        content= {
                            "comand":"chat_message",
                            "restrict_message": "you have been Blocked from sending message",
                            "is_user_restricted":True,
                            "message":[]
                        }
                        return self.send_message_to_group(content)
            else:
                if data["replyid"] is not None:
                    reply_message = Message.objects.get(id=data["replyid"])
                    message = Message.objects.create(contact=user_contact,content=data["message"],reply=reply_message)
                    friend_chat[0].messages.add(message)
                    friend_chat[0].save()
                    content= {
                    "comand":"chat_message",
                    "is_user_restricted":False,
                    "message":self.messages_json(message)
                    }
                    return self.send_message_to_group(content)
                else:
                    message = Message.objects.create(contact=user_contact,content=data["message"])
                    friend_chat[0].messages.add(message)
                    friend_chat[0].save()
                    content= {
                    "comand":"chat_message",
                    "is_user_restricted":False,
                    "message":self.messages_json(message)
                    }
                    return self.send_message_to_group(content)


                
                
                

            
            
        else:
            print(data["chaturl"])
            author_name = data["from"]
            user_model = user.objects.filter(username=author_name)[0]
            # getting contact
            get_contact , created = Contact.objects.get_or_create(user=user_model)
            get_chat = Chat.objects.get(chat_slug=data["chaturl"])
            if get_contact in get_chat.restrict.all():
                content= {
                "comand":"chat_message",
                "restrict_message":"you have been restricted for chating in this room",
                "is_user_restricted":True,
                "message":[]
                }
                return self.send_message_to_group(content)
            else:
                if data["replyid"] is not None:
                    reply_message = Message.objects.get(id=data["replyid"])
                    message = Message.objects.create(contact=get_contact,content=data["message"],reply=reply_message)
                    get_chat.messages.add(message)
                    get_chat.save()
                    content= {
                    "comand":"chat_message",
                    "is_user_restricted":False,
                    "message":self.messages_json(message)
                    }
                    return self.send_message_to_group(content)
                else:
                    message = Message.objects.create(contact=get_contact,content=data["message"])
                    get_chat.messages.add(message)
                    get_chat.save()
                    content= {
                    "comand":"chat_message",
                    "is_user_restricted":False,
                    "message":self.messages_json(message)
                    }
                    return self.send_message_to_group(content)

            
            #get_chat = get_object_or_404(Chat,)
            
           
            
            
            

        

    command = {
        "fetch_message": fetch_message,
        "send_chat_message": send_chat_message,
    }

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        print(text_data)
        text_data_json = json.loads(text_data)
        #message = text_data_json["message"]
        self.command[text_data_json["comand"]](self,text_data_json)


        # Send message to room group
    def send_message_to_group(self,data):    
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": data}
        )

    def fetch_message_to_group(self,data):    
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": data}
        )

    def send_message(self, message):
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))