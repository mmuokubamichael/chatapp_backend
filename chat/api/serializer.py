from rest_framework import serializers
from chat.models import Chat,Contact,FriendsChat,OnlineforChannels
import uuid


def generate_unique_id():
    random_uuid = uuid.uuid4()
    unique_id = str(random_uuid.int)[:4]
    return unique_id

class ContactSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value

class ChatSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many = True)
    class Meta:
        model = Chat
        fields = ('id',"participants","admin","restrict","messages","chat_name","chat_slug","image")
        read_only = ('id')


    def create(self,validated_data):
        print(validated_data)
        participants = validated_data.pop("participants")
        slug = "c"+validated_data["chat_name"] + "_" + generate_unique_id()
        chat = Chat(chat_name=validated_data["chat_name"],chat_slug=slug)
        chat.save()
        print("working")
        user_contact = Contact.objects.get(user__username = participants[0])
        chat.participants.add(user_contact)
        chat.admin.add(user_contact)
        chat.save()
        onlineuserstatus = OnlineforChannels.objects.get_or_create(group=chat,participant=user_contact)
        return chat



class UserContactSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = Contact
        fields = ('id','user','friends','slug','online','image')
        read_only = ('id')



class FriendSerializer(serializers.ModelSerializer):
    sender = UserContactSerializer()
    reciever = UserContactSerializer()
    class Meta:
        model = FriendsChat
        fields = ('id','sender','messages','reciever','accepted','slug')
        read_only = ('id')

