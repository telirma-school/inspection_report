from django.shortcuts import render,HttpResponse,redirect
from .models import Article,Produits,Client,RapportItem
from .models import Rapport as RapportVerif
from django.views import View
from .form import ProduitForm,Rapport_item_form, SignUpForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
import datetime
from django.contrib.auth.models import User
#=== importation pour generer fichier pdf
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from .pdf_rapport import generer_rapport_pdf

# Create your views here.

#=======================================
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        #authentification
        user = authenticate(request,username=username,password=password)
        # on cree un logique pour la verification de l'utilisateur
        #on verifie si l'utilisateur existe, si oui on appelle la fonction 
        if user is not None:
            login(request,user)
            messages.success(request,"You are loggin")
            return redirect('article:home')
        else:
            messages.success(request,"You are not loggin / there an error")
            return redirect('article:login')


    return render(request,'login.html')


def logout_user(request):
    logout(request)
    messages.success(request,"You have been logout")
    return redirect('article:home')


#==================================


def home(request):
	#la commande suivante cas dans la bd(le models) et recupere les donnes suivant le filtrage de la commande
    liste_produits = Produits.objects.all()
	#la commande suivante crais une variable de contex, et lui affecte un dictionnaire contenant les element recupere de la bd
    context = {"liste_produits":liste_produits}
    #dans la fction return, on choisi la methode render, on lui envoit comme arguement : les requetes - le template qui a besoin d'etre envoyer a l'utilisateur  - et enfin les variable de contexte qui seront afficher 
    return render(request,'home.html',context)


def boutique(request):
	#la commande suivante cas dans la bd(le models) et recupere les donnes suivant le filtrage de la commande
    liste_produits = Produits.objects.all()
	#la commande suivante crais une variable de contex, et lui affecte un dictionnaire contenant les element recupere de la bd
    context = {"liste_produits":liste_produits}
    #dans la fction return, on choisi la methode render, on lui envoit comme arguement : les requetes - le template qui a besoin d'etre envoyer a l'utilisateur  - et enfin les variable de contexte qui seront afficher 
    return render(request,'boutique.html',context)

def crm(request):
	#la commande suivante cas dans la bd(le models) et recupere les donnes suivant le filtrage de la commande
    liste_client = Client.objects.all()
    liste_rapport = RapportVerif.objects.all()
    liste_rapport_item = RapportItem.objects.all()
	#la commande suivante crais une variable de contex, et lui affecte un dictionnaire contenant les element recupere de la bd
    context = {"liste_client":liste_client,
               "liste_rapport":liste_rapport,"liste_rapport_item":liste_rapport_item}
    #dans la fction return, on choisi la methode render, on lui envoit comme arguement : les requetes - le template qui a besoin d'etre envoyer a l'utilisateur  - et enfin les variable de contexte qui seront afficher 
    return render(request,'crm.html',context)



def blog(request):
    liste_article = Article.objects.all()
    context = {
        "liste_article":liste_article
    }
    return render(request,'blog.html',context)


class createArticle(View):
    def get(self,request, *args, **kwargs):
        return render(request,'article/create_article.html')
    

    def post(self, request, *args, **kwargs):
        try:
            titre = request.POST.get('titre')
            auteur = request.POST.get('auteur')
            contenu = request.POST.get('contenu')
            date = request.POST.get('date')

            article = Article(titre=titre,auteur=auteur,contenu=contenu,date=date)
            article.save()
            messages.success(request,"Article enregistré avec succes")
            return redirect('article:createArticle')
        except Exception as e:
            messages.success(request,"Erreur lors de l'enregistrement de lArticle")
            #return redirect('article:home')
            return render(request,'article/create_article.html')


class createProduit(View):
     
    def get(self,request, *args, **kwargs):
        form = ProduitForm()
        return render(request,'produit/create_produit.html',{'form':form})
    

    def post(self, request, *args, **kwargs):
        
        if request.method == 'POST':
            form = ProduitForm(request.POST,request.FILES)
        
            if form.is_valid(): 
                form.save()
                messages.success(request,"Produit enregistré avec succes")
                return redirect('article:home')
            else:
                return render(request,'produit/create_produit.html',{'form':form})
        else:
            form = ProduitForm()
            messages.success(request,"Erreur lors de l'enregistrement du Produit")
            return render(request,'produit/create_produit.html',{'form':form})


class createRapport(View):
    
    def get(self,request, *args, **kwargs):
        liste_client = Client.objects.all()
        liste_rapport = RapportVerif.objects.all()
        liste_rapport_item = RapportItem.objects.all()
            #la commande suivante crais une variable de contex, et lui affecte un dictionnaire contenant les element recupere de la bd
        context = {'liste_client':liste_client,
                    'liste_rapport':liste_rapport,'liste_rapport_item':liste_rapport_item}
            #dans la fction return, on choisi la methode render, on lui envoit comme arguement : les requetes - le template qui a besoin d'etre envoyer a l'utilisateur  - et enfin les variable de contexte qui seront afficher 
            

        return render(request,'produit/create_rapport.html',context)
    

    def post(self, request, *args, **kwargs):
        liste_client = Client.objects.all()
        liste_rapport = RapportVerif.objects.all()
        liste_rapport_item = RapportItem.objects.all()
            #la commande suivante crais une variable de contex, et lui affecte un dictionnaire contenant les element recupere de la bd
        context = {'liste_client':liste_client}
                    #'liste_rapport':liste_rapport,'liste_rapport_item':liste_rapport_item}
            #dans la fction return, on choisi la methode render, on lui envoit comme arguement : les requetes - le template qui a besoin d'etre envoyer a l'utilisateur  - et enfin les variable de contexte qui seront afficher 
            

        try:
            titre = request.POST.get('titre')
            client_name = request.POST.get('client')
            date_verification = request.POST.get('date_verification')
            create_at = request.POST.get('create_at')
            client = Client.objects.get(name=client_name)
            rapport = RapportVerif(date_verification=date_verification,titre=titre,client=client,create_at=create_at)
            rapport.save()
            messages.success(request,"Rapport crée avec succes")
            dernier_rapport = RapportVerif.objects.order_by('-id').first()
            return redirect('article:crm')
        except Exception as e:
            messages.success(request,f"=={e}==Erreur lors de la creation du rapport")
            #return redirect('article:home')
            return render(request,'produit/create_rapport.html',context)
#=============

#=======================
class contenuRapport(View):
	#definition de la methode get pour notre page et notre formulaire
    def get(self,request,rapport_number):
    #la commande suivante cas dans la bd(le models) et recupere les donnes suivant le filtrage de la commande
        liste_client = Client.objects.all()
        user = User.objects.all()
        rapport_courant = RapportVerif.objects.get(rapport_number=rapport_number)
        rapport_id = rapport_courant.id
        liste_rapport_item = RapportItem.objects.filter(rapport_id=rapport_id)
        #========================================
        form = Rapport_item_form
        context = {"user":user,"liste_client":liste_client,'form':form,
                "rapport_courant":rapport_courant,"liste_rapport_item":liste_rapport_item}
     
        return render(request,'produit/contenu_rapport.html',context)
    #***********************************
    def post(self, request, *args, **kwargs):
        try:
            
            rapport_id = request.POST.get('rapport')
            emplacement = request.POST.get('emplacement')
            type_appareil = request.POST.get('type_appareil')
            statut_appareil = request.POST.get('statut_appareil')
            observation = request.POST.get('observation')
            


            rapport_item = RapportItem(rapport_id = rapport_id,emplacement=emplacement,
                                    type_appareil=type_appareil,statut_appareil=statut_appareil,observation=observation)
            rapport_item.save()


            liste_client = Client.objects.all()
            
            
            liste_rapport_item = RapportItem.objects.filter(rapport_id=rapport_id)
           
            rapport_courant = RapportVerif.objects.get(id=rapport_id)
            rapport_number = rapport_courant.rapport_number

            
            
            form = Rapport_item_form
            context = {"liste_client":liste_client,'form':form,'rapport_number':rapport_number,
                "rapport_courant":rapport_courant,"liste_rapport_item":liste_rapport_item}
     
            messages.success(request,"item du present rapport enregistré avec succes")
            return render(request,'produit/contenu_rapport.html',context)
        
        except Exception as e:
            rapport_id= request.POST.get('rapport')
            rapport_courant = RapportVerif.objects.get(id=rapport_id)
            rapport_number = rapport_courant.rapport_number
            messages.success(request,"Erreur lors de l'enregistrement de cet item")
            #return redirect('article:home')
            return render(request,'article:contenuRapport',rapport_number = rapport_number)

    #=============================================

#============================

def detail_client(request,nom):
	#la commande suivante cas dans la bd(le models) et recupere les donnes suivant le filtrage de la commande
    client_data = Client.objects.get(name=nom)
    client_id = client_data.id
    rapport_client = RapportVerif.objects.filter(client_id = client_id)
    #la commande suivante crais une variable de contex, et lui affecte un dictionnaire contenant les element recupere de la bd
    context = {"client_data":client_data,
               "rapport_client":rapport_client}#dans la fction return, on choisi la methode render, on lui envoit comme arguement : les requetes - le template qui a besoin d'etre envoyer a l'utilisateur  - et enfin les variable de contexte qui seront afficher 
    return render(request,'detail_client.html',context)


#=============================
# vue pour la modification d'un item du rapport
def modifie_item_rapport(request,pk):
    item_rapport = RapportItem.objects.get(id=pk)
    context = {'item_rapport' : item_rapport }
       

    
    if request.method == 'POST':
        rapport_id = request.POST.get('rapport')
        emplacement = request.POST.get('emplacement')
        type_appareil = request.POST.get('type_appareil')
        statut_appareil = request.POST.get('statut_appareil')
        observation = request.POST.get('observation')
    
        rapport_item = RapportItem(id=pk,rapport_id = rapport_id,emplacement=emplacement,
                            type_appareil=type_appareil,statut_appareil=statut_appareil,observation=observation)
    
        rapport_item.save()

        rapport_courant = RapportVerif.objects.get(id=rapport_id)
        rapport_number = rapport_courant.rapport_number

        context = {'rapport_number':rapport_number}
        messages.success(request,"item du present rapport enregistré avec succes")
        return redirect('article:contenuRapport',rapport_number)

    
    return render(request,'modifie_item_rapport.html',context)

def delete_item_rapport(request,pk,rapport_number):
    item_courant = RapportItem.objects.get(id=pk)
    item_courant.delete()
    messages.success(request,"cet item a été effacé avec succes")
    return redirect('article:contenuRapport',rapport_number)
        






#=============================
# vue pour la modification d'un rapport
def modifie_rapport(request,pk):
    rapport = RapportVerif.objects.get(id=pk)
    context = {'rapport' : rapport }
       

    
    if request.method == 'POST':
        rapport_id = pk
        client_id = rapport.client_id
        rapport_number = request.POST.get('rapport_number')
        client = Client.objects.get(id=client_id)
        titre = request.POST.get('titre')
        create_at = rapport.create_at
        update_at = datetime.date.today()
        date_verification = request.POST.get('date_verification')
    
        rapport_up = RapportVerif(rapport_number=rapport_number,id=pk ,update_at = update_at,date_verification=date_verification,titre=titre,client=client,create_at=create_at)
        rapport_up.save()

        liste_client = Client.objects.all()
        liste_rapport = RapportVerif.objects.all()

        context = {"liste_client":liste_client,
               "liste_rapport":liste_rapport}
    
        messages.success(request,"Rapport modifié avec succes")
        return render(request,'crm.html',context)

    
    return render(request,'modifie_rapport.html',context)

#==================================
#===== creation de compte utilisateur

class register_user(View):
     
    def get(self,request, *args, **kwargs):
        form = SignUpForm()
        return render(request,'register.html',{'form':form})
    

    def post(self, request, *args, **kwargs):
        
        if request.method == 'POST':
            form = SignUpForm(request.POST)
        
            if form.is_valid(): 
                form.save()
                messages.success(request,"compte enregistré avec succes")
                return redirect('article:login')
            else:
                return render(request,'register.html',{'form':form})
        else:
            form = SignUpForm()
            messages.success(request,"Erreur lors de l'enregistrement du compte")
            return render(request,'register.html',{'form':form})





def rapport_pdf(request, rapport_number):
    return generer_rapport_pdf(request, rapport_number)




#==============================================================

    # p.showPage()
    # p.save()


    buffer.seek(0)

    rapport = RapportVerif.objects.get(rapport_number=rapport_number)
    client_name = rapport.client.name
    return FileResponse(buffer,as_attachment=True,filename=f"{client_name}_{rapport_number}.pdf")