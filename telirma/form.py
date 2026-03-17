from django import forms
from .models import Produits, RapportItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import datetime

# ✅ Liste de tuples (valeur_bd, label_affiché)
FONCTION_CHOICES = [
    ("INSPECTEUR", "Inspecteur"),
    ("COMPTABLE",  "Comptable"),
]

SEXE_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
]


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    first_name = forms.CharField(
        label="", max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    last_name = forms.CharField(
        label="", max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prenom'
        })
    )
    function = forms.ChoiceField(
        choices=FONCTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # ✅ CORRECTION : widget=forms.DateInput() au lieu de widget=datetime (module)
    date_de_naissance = forms.DateField(
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    sexe = forms.ChoiceField(
        choices=SEXE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # ✅ CORRECTION : required=False (booléen) et non required='False' (string truthy)
    photo_de_profil = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'function', 'date_de_naissance', 'photo_de_profil',
            'sexe', 'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom d'utilisateur"
            }),
        }


class ProduitForm(forms.ModelForm):

    prix = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Prix en FCFA'
        })
    )

    class Meta:
        model = Produits
        fields = ['nom', 'description', 'prix', 'image']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du produit'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du produit'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_prix(self):
        prix = self.cleaned_data.get('prix')
        if not prix or prix <= 0:
            raise forms.ValidationError('Le prix doit être supérieur à zéro.')
        return prix


class Rapport_item_form(forms.ModelForm):

    class Meta:
        model = RapportItem
        fields = '__all__'
