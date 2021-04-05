from django.urls import path, re_path, include
from . import views


urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post_create/', views.PostCreate.as_view(), name='post_create'),
    path('blog/<int:id>/<slug:slug>/', views.post_detail, name='post_detail'),
    path('like/', views.like_post, name='like_post'),
    path('post_edit/<int:pk>/', views.PostEdit.as_view(), name='post_edit'),
    path('post_delete/<int:pk>/', views.PostDelete.as_view(), name='post_delete'),
    path('global_search/', views.GlobalSearch.as_view(), name='global_search'),
    path('edit_profile/', views.edit_profile, name='edit_profile')
]