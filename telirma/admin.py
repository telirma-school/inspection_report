from django.contrib import admin
from .models import Produits,Article,Record,Client
from .models import Rapport,RapportItem
# Register your models here.


#si je veux que mes produits s'affiche sous formes de lignes
# admin.site.register(Produits)
admin.site.register(RapportItem)


#si je veux que mes element s'affiche dans le dashboard sous forme de table
@admin.register(Produits)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom','prix','description','image')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre','auteur','date')
	
	
@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('create_at','first_name','last_name','email')

@admin.register(Rapport)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('create_at','rapport_number','client')


@admin.register(Client)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('name','phone_number','email')