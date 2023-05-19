from django.urls import path
from .views import (ChatListView,ChatCreateView,joinChat,FriendListView,addFriend,deleteFriend,
                    acceptfriendrequest,rejectFriendRequest,unreadMessagesChannels,updateOnlinechatState,updateProfileImage
                    ,getUserProfileImage,deleteProfileImage,exitGroup,restrictUser,unrestrictUser,blockUser,unblockUser)


app_name = "chat"
urlpatterns = [
    path('',ChatListView.as_view()),
    path('friends/',FriendListView.as_view()),
    path('createchat/',ChatCreateView.as_view()),
    path('updatechat/<slug>/',joinChat),
    path('friendrequest/<slug>/',addFriend),
    path('deleterequest/<slug>/',deleteFriend),
    path('acceptrequest/<slug>/',acceptfriendrequest),
    path('rejectrequest/<slug>/',rejectFriendRequest),
    path('unreadchatmessage/<slug>/',unreadMessagesChannels),
    path('sendonlinechatstatus/<slug>/',updateOnlinechatState),
    path('updateprofile/<slug>/',updateProfileImage),
    path('getprofileimage/<slug>/',getUserProfileImage),
    path('deleteProfileImage/<slug>/',deleteProfileImage),
    path('exitgroup/<slug>/',exitGroup),
    path('restrictUser/<slug>/',restrictUser),
    path('unrestrictUser/<slug>/',unrestrictUser),
    path('blockUser/<slug>/',blockUser),
    path('unblockUser/<slug>/',unblockUser),
    
]