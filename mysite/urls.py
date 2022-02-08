from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from rest_framework import routers
from blog import views

router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)
router.register(r'company', views.CompanyViewSet)
router.register(r'server', views.ServerViewSet)

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path('accounts/', include('django.contrib.auth.urls')),    url(r'^admin/', admin.site.urls),
    url(r'', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls'))
]
