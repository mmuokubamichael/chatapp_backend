from rest_framework import permissions
from rest_framework.generics import (ListAPIView,RetrieveAPIView,CreateAPIView,DestroyAPIView,UpdateAPIView)
from rest_framework.decorators import api_view


from chat.models import Chat,Contact,FriendsChat,OnlineforChannels,Onlineforfriend
from .serializer import ChatSerializer,FriendSerializer,UserContactSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Q
import uuid
import os
import cloudinary.uploader
from django.utils.decorators import method_decorator
from corsheaders.decorators import cors_headers

def generate_unique_id():
    random_uuid = uuid.uuid4()
    unique_id = str(random_uuid.int)[:7]
    return unique_id



user = get_user_model()


def get_user_contact(username):
    current_user= get_object_or_404(user,username=username)
    user_contact = get_object_or_404(Contact,user=current_user)
    return user_contact



@method_decorator(cors_headers(), name='dispatch')
class ChatListView(ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny,)
    def get_queryset(self):
        queryset = Chat.objects.all()
        username = self.request.query_params.get('username',None)
        if username is not None:
            contact = get_user_contact(username)
            get_user_chats = contact.chats.all()
        return get_user_chats

@method_decorator(cors_headers(), name='dispatch')
class FriendListView(ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = (permissions.AllowAny,)
    def get_queryset(self):
        queryset = FriendsChat.objects.all()
        username = self.request.query_params.get('username',None)
        if username is not None:
            contact = get_user_contact(username)
            user_friends = FriendsChat.objects.filter(Q(sender=contact)|Q(reciever=contact))
        return user_friends

@cors_headers()  
@api_view(['PUT',])
def joinChat(request,slug):
    print(request.data["participants"])
    get_chat=Chat.objects.get(chat_slug=slug)
    get_user_contact = Contact.objects.get(user__username = request.data["participants"])
    get_chat.participants.add(get_user_contact)
    get_chat.save()
    user_online,_ = OnlineforChannels.objects.get_or_create(group=get_chat,participant=get_user_contact)
    serializer_class = ChatSerializer(get_chat)
    return Response(serializer_class.data)

@cors_headers() 
@api_view(['PUT',])
def addFriend(request,slug):
    user=request.data["currentuser"]
    friend=slug[1:]
    userContact = Contact.objects.get(user__username=user)
    friendContact = Contact.objects.get(user__username=friend)
    userContact.friends.add(friendContact)
    friendContact.friends.add(userContact)
    friendChat,created = FriendsChat.objects.get_or_create(sender=userContact,reciever=friendContact)
    onlineuserStatus,created= Onlineforfriend.objects.get_or_create(friendchat=friendChat,participant=userContact)
    onlineFriendStatus,created= Onlineforfriend.objects.get_or_create(friendchat=friendChat,participant=friendContact)
    serializer_friend = FriendSerializer(friendChat)
    return Response(serializer_friend.data)

@cors_headers() 
@api_view(['POST',])
def deleteFriend(request,slug):
    print(request.data)
    user=request.data["currentuser"]
    friend=slug[1:]
    userContact = Contact.objects.get(user__username=user)
    friendContact = Contact.objects.get(user__username=friend)
    userContact.friends.remove(friendContact)
    friendContact.friends.remove(userContact)
    friendChat = FriendsChat.objects.filter(sender=userContact,reciever=friendContact)
    print(friendChat)
    if friendChat.exists():
        onlineuserStatus= Onlineforfriend.objects.filter(friendchat=friendChat[0],participant=userContact)
        onlineFriendStatus= Onlineforfriend.objects.filter(friendchat=friendChat[0],participant=friendContact)
        onlineuserStatus[0].delete()
        onlineFriendStatus[0].delete()
        print("deleted")
        serializer_friend = FriendSerializer(friendChat[0])
        friendChat[0].delete()
        return Response(serializer_friend.data)
    return JsonResponse({"deleted":"ok"})

@cors_headers() 
@api_view(['PUT',])
def acceptfriendrequest(request,slug):
    print(request.data)
    print(slug)
    user=request.data["currentuser"]
    friend=slug[1:]
    userContact = Contact.objects.get(user__username=user)
    friendContact = Contact.objects.get(user__username=friend)
    friendChat = FriendsChat.objects.get(sender=friendContact,reciever=userContact)
    friendChat.accepted = True
    friendChat.slug = "_friend"+generate_unique_id()
    friendChat.save()
    
    serializer_friend = FriendSerializer(friendChat)
    return Response(serializer_friend.data)

@cors_headers() 
@api_view(['POST',])
def rejectFriendRequest(request,slug):
    print(request.data)
    user=request.data["currentuser"]
    friend=slug[1:]
    userContact = Contact.objects.get(user__username=user)
    friendContact = Contact.objects.get(user__username=friend)
    userContact.friends.remove(friendContact)
    friendContact.friends.remove(userContact)
    friendChat = FriendsChat.objects.filter(sender=friendContact,reciever=userContact)
    if friendChat.exists():

        onlineuserStatus= Onlineforfriend.objects.get(friendchat=friendChat[0],participant=userContact)
        onlineFriendStatus= Onlineforfriend.objects.get(friendchat=friendChat[0],participant=friendContact)
        onlineuserStatus.delete()
        onlineFriendStatus.delete()
        serializer_friend = FriendSerializer(friendChat[0])
        friendChat[0].delete()
        return Response(serializer_friend.data)
    return JsonResponse({"deleted":"ok"})
    
@method_decorator(cors_headers(), name='dispatch')    
class ChatCreateView(CreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated, )

@cors_headers() 
@api_view(['GET',])
def unreadMessagesChannels(request,slug):
    userContact = Contact.objects.get(user__username=slug)
    allchat = Chat.objects.all()
    friendschat = FriendsChat.objects.filter(Q(sender=userContact)|Q(reciever=userContact))
    data = {}
    channel=[]
    friend_ = []
    for chat in allchat:
        if userContact in chat.participants.all():
            contact_is_online = OnlineforChannels.objects.get(group=chat,participant=userContact)
            counter = 0
            
            for mess in chat.messages.all():
                print(contact_is_online.online,mess.timestamp)
                if mess.timestamp > contact_is_online.online:
                    print("counter")
                    counter +=1
                    

            channel.append({str(chat.chat_slug):counter})

    
    if friendschat.exists():
        for friend in friendschat:
            print(friend)
            onlinefriend = Onlineforfriend.objects.get(friendchat=friend,participant=userContact)
            counter = 0
            for mess in friend.messages.all():
                if onlinefriend.online < mess.timestamp:
                    counter +=1
            friend_.append({str(friend.slug):counter})
    data["channel"] = channel
    data["friend"] = friend_      

    return JsonResponse({"unreadChat":data})

@cors_headers() 
@api_view(['PUT',])
def updateOnlinechatState(request,slug):
    user=request.data["currentuser"]
    if slug[0] == "c":
        userContact = Contact.objects.get(user__username=user)
        getChat = Chat.objects.filter(chat_slug=slug)
        if getChat.exists():
            getUserOnlineStatus = OnlineforChannels.objects.get(group=getChat[0],participant=userContact)
            getUserOnlineStatus.save()
            return JsonResponse({"unreadChat":"ok"})
    elif slug[0] == "_":
        userContact = Contact.objects.get(user__username=user)
        getfriend = FriendsChat.objects.filter(slug=slug)
        
        if getfriend.exists():
            getUserOnlineStatus = Onlineforfriend.objects.get(friendchat=getfriend[0],participant=userContact)
            getUserOnlineStatus.save()
            return JsonResponse({"unreadChat":"ok"})
    return JsonResponse({"unreadChat":"error"})

@cors_headers() 
@api_view(['PUT',])
def updateProfileImage(request,slug):
    print(request.data)
    if slug[0] == "c":
        userChat = Chat.objects.get(chat_slug=slug)
        if "image" in request.data.keys():
            print("yessssssssssssss")
            if userChat.image:
                print("simaggggggggg")
                #os.remove(userChat.image.path)

        
        serializer = ChatSerializer(instance=userChat, data=request.data, many=False, partial="True")
        print("sucesss")
        if serializer.is_valid():
            serializer.save()
            print("sucesss")
            return JsonResponse({"saveImage":"success"})
        return Response(serializer.errors)
    else:
        userContact = Contact.objects.get(user__username=slug)
        if userContact.image:
            #os.remove(userContact.image.path)
            X="y"
        serializer = UserContactSerializer(instance=userContact, data=request.data, many=False, partial="True")
        print("sucesss")
        if serializer.is_valid():
            serializer.save()
            print("sucesss")
            return JsonResponse({"saveImage":"success"})
        return Response(serializer.errors)

@cors_headers() 
@api_view(['DELETE',])
def deleteProfileImage(request,slug):
    userContact = Contact.objects.get(user__username=slug)
    if len(userContact.image)>0:
        userContact.image.delete(save=True)
    serializer = UserContactSerializer(userContact)
    print("sucesss")
    return Response(serializer.data)

@cors_headers() 
@api_view(['GET',])
def getUserProfileImage(request,slug):
    userContact = Contact.objects.get(user__username=slug)
   
    serializer = UserContactSerializer(userContact)
    return Response(serializer.data)

@cors_headers() 
@api_view(['POST',])
def exitGroup(request,slug):
    print(request.data)
    user=request.data["currentuser"]
    
    userContact = Contact.objects.get(user__username=user)
    groupChat = Chat.objects.get(chat_slug=slug)
    if userContact in groupChat.participants.all():
        userGrouponline = OnlineforChannels.objects.get(group=groupChat,participant=userContact)
        groupChat.participants.remove(userContact)
        userGrouponline.delete()
        if userContact in groupChat.admin.all():
            groupChat.admin.remove(userContact)

        return JsonResponse({"removed":"success"})
    return JsonResponse({"removed":"error"})

@cors_headers() 
@api_view(['POST',])
def restrictUser(request,slug):
    user=request.data["currentuser"]
    
    userContact = Contact.objects.get(user__username=user)
    groupChat = Chat.objects.get(chat_slug=slug)
    groupChat.restrict.add(userContact)
    groupChat.save()
    return JsonResponse({"restricted":userContact.user.username})


@cors_headers() 
@api_view(['POST',])
def unrestrictUser(request,slug):
    user=request.data["currentuser"]
    userContact = Contact.objects.get(user__username=user)
    groupChat = Chat.objects.get(chat_slug=slug)
    groupChat.restrict.remove(userContact)
    groupChat.save()
    return JsonResponse({"unrestricted":userContact.user.username})


@cors_headers() 
@api_view(['POST',])
def blockUser(request,slug):
    user=request.data["currentuser"]
    userContact = Contact.objects.get(user__username=user)
    friend_chat = FriendsChat.objects.get(slug=slug)
    if userContact == friend_chat.sender:
        friend_chat.restrict.add(friend_chat.reciever)
    else:
        friend_chat.restrict.add(friend_chat.sender)
    return JsonResponse({"blocked":"success"})


@cors_headers() 
@api_view(['POST',])
def unblockUser(request,slug):
    user=request.data["currentuser"]
    userContact = Contact.objects.get(user__username=user)
    friend_chat = FriendsChat.objects.get(slug=slug)
    if userContact == friend_chat.sender:
        friend_chat.restrict.remove(friend_chat.reciever)
    else:
        friend_chat.restrict.remove(friend_chat.sender)
    return JsonResponse({"unblocked":"success"})