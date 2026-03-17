from django.db import models
from django.conf import settings 
from datetime import datetime
from django.contrib.auth.models import User

# Create your models here.
class Article(models.Model):
    titre = models.CharField(max_length=100)
    auteur = models.CharField(max_length=42)
    contenu = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True, auto_now=False,
                                verbose_name="Date de parution")
    
    def __str__(self):
        return self.titre
    

class Produits(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    prix = models.FloatField()
    image = models.ImageField(upload_to='images/')
    incre = 0


    def __str__(self):
        return self.nom
	
    def get_image_url(self):
         if self.image:
              return self.image.url
         else:
              return None
         
		
		
class Record(models.Model):
	create_at = models.DateTimeField(auto_now_add=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email = models.CharField(max_length=50)
	phone = models.CharField(max_length=50)
	address = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=50)
	zipcode = models.CharField(max_length=50)
	
	def __str__(self):
		return(f"{self.first_name } {self.last_name}")
		

class Client(models.Model):
    name = models.CharField(max_length=200)
    #client_number = models.CharField(max_length=50, unique=True,default=generate_client_reference)
    address = models.TextField()
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name
#==========================================================
# cration de la variable pour generer les numero de rapport

def generate_rapport_reference():
     prefix  = "RPRT"
     today = datetime.now()

     dernier_rapport = Rapport.objects.order_by('-id').first()
     if dernier_rapport:
        try:
            last_number = int(dernier_rapport.rapport_number.split('-')[-1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
     else:
        next_number = 1
     return f"{prefix}-{today.year}-{today.month}-{next_number:04d}"#example : RPRT-2025-10-0001

class Rapport(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL,null=True)
    rapport_number = models.CharField(max_length=50, unique=True,default=generate_rapport_reference)
    create_at = models.DateField(auto_now_add=True)
    date_verification = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now_add=True)
    titre = models.CharField(max_length=200, default="Rapport sans titre")
    #create_by = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    verification_realiser_par = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    

    def __str__(self):
        return f"Rapport #{self.rapport_number} for {self.client.name if self.client else 'N/A'}"


#========================================================================
class RapportItem(models.Model):
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE, related_name='items')
    emplacement = models.CharField(max_length=255) # Can be used if not linking to a Product
    type_appareil = models.CharField(max_length=255) # Can be used if not linking to a Product
    statut_appareil = models.CharField(max_length=255) # Can be used if not linking to a Product
    observation = models.CharField(max_length=255) # Can be used if not linking to a Product
    

    def __str__(self):
        return f"Un extincteur {self.type_appareil} se trouve à l'emplacement: {self.emplacement}, son statut est  : {self.statut_appareil}"
	

#===================================== creation des type d'extincteur
# class Extincteur(models.Model):
#     titre = models.CharField(max_length=100)
#     type = models.CharField(max_length=100)

#     def __str__(self):
#         return self.titre

# class Etat_extincteur(models.Model):
#     extincteur = models.ForeignKey(Extincteur, on_delete=models.CASCADE, related_name='appareil')
#     etat_appareil = models.CharField(max_length=100)

#     def __str__(self):
#         return self.titre


#=====================
#======= profil pour utilisateurs

class Profil(models.Model):
     user = models.OneToOneField(User,on_delete=models.SET_NULL,null="True")#liaison du profil au model user
     function = models.CharField()
     date_de_naissance = models.DateField(auto_now_add=True)
     sexe = models.CharField(max_length=1)
     photo_profil = models.ImageField(null=True,blank=True,upload_to="photo_profil/")
