from django.contrib import admin
from .models import Post, Comentario

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['autor', 'data_criacao', 'curtidas_count']
    list_filter = ['data_criacao']
    search_fields = ['autor__username', 'conteudo']
    
    def curtidas_count(self, obj):
        return obj.curtidas.count()
    curtidas_count.short_description = 'Curtidas'

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['autor', 'post', 'data_criacao']
    list_filter = ['data_criacao']
    search_fields = ['autor__username', 'texto']
