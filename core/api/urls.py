from home.views import index, people, PersonAPI, PeopleViewSet, RegisterAPI, LoginAPI
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'people',PeopleViewSet,basename='person')


urlpatterns = [
    path('register/',RegisterAPI.as_view()),
    path('login/', LoginAPI.as_view()),

    path('', include(router.urls)),
    path('index/', index),
    path('people/', people),
    path('persons/', PersonAPI.as_view()),
]