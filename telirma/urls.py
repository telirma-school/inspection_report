

from django.urls import path
from .import views
from .views import createArticle, register_user
from .views import createProduit,contenuRapport
from .views import createRapport

app_name = 'article'

urlpatterns = [
    # page d'acceuil du site
    path('',views.home,name='home'),
    # bloc du site
    path('blog/', views.blog,name='blog'),
    # creation d'un nouvel article
    path('create-article/',createArticle.as_view(),name='createArticle'),
    path('create-produit/',createProduit.as_view(),name='createProduit'),
    path('boutique/',views.boutique,name='boutique'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('crm/',views.crm,name='crm'),
    #creation du rapport
    path('create-rapport/',createRapport.as_view(),name='createRapport'),
    #path('create-rapport/',views.createRapport,name='createRapport'),
    # affichage du rapport, le lien doit contenir l'identifiant du rapport

    #path('contenuRapport/<str:rapport_number>',views.contenuRapport,name='contenuRapport'),
    path('contenuRapport/<str:rapport_number>',contenuRapport.as_view(),name='contenuRapport'),
    
    #============================
    # afficher les detai client  detailclient/(?P<pk>[0-9]+)\\Z
    #path('detailclient/<int:pk>',views.detail_client,name='detailClient'),
    path('detailclient/<str:nom>',views.detail_client,name='detailClient'),
    # creation des item de rapport
    #path('create_rapport_item/',views.Create_rapport_item,name='create_rapport_item'),
    #================
    # chemin pour visualiser un item du rapport et le modifier
    path('modifie_item_rapport/<int:pk>',views.modifie_item_rapport,name='modifie_item_rapport'),
    # chemin pour effacer un item du rapport et le modifier
    path('delete_item_rapport/<int:pk>,<str:rapport_number>',views.delete_item_rapport,name='delete_item_rapport'),
     # chemin pour visualiser un rapport et le modifier
    path('modifie_rapport/<int:pk>',views.modifie_rapport,name='modifie_rapport'),
     # chemin pour visualiser un rapport en pdf
    path('rapport_pdf/<str:rapport_number>',views.rapport_pdf,name='rapport_pdf'),
     # chemin pour vcreation de compte utilisateur
    path('register/',register_user.as_view(),name='register'),
    
]

