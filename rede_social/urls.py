from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from core.views import index
from mensagens.views import chat_view
# Handlers de erro
handler404 = core_views.erro_404
handler500 = core_views.erro_500
handler403 = core_views.erro_403
handler400 = core_views.erro_400


urlpatterns = [

    path('', index, name='home'),  # ⬅ rota para a página inicial
    
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('mensagens/', include('mensagens.urls', namespace='mensagens')),
    
]

if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    from django.views.static import serve
    from django.urls import re_path

    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
