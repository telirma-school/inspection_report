# TELIRMA — Guide de mise à jour des templates

## Contenu de cette livraison

Ce dossier contient tous les templates HTML redesignés pour l'application Django TELIRMA, ainsi que les fichiers Python corrigés.

---

## Installation rapide

### 1. Remplacer les templates

Copiez tout le contenu du dossier `templates/` dans votre dossier `facebook/templates/` en écrasant les anciens fichiers.

```
facebook/
└── templates/
    ├── main.html              ← REMPLACER
    ├── navbar.html            ← REMPLACER
    ├── footer.html            ← REMPLACER
    ├── message.html           ← REMPLACER
    ├── login.html             ← REMPLACER
    ├── register.html          ← REMPLACER
    ├── home.html              ← REMPLACER
    ├── boutique.html          ← REMPLACER
    ├── blog.html              ← REMPLACER
    ├── crm.html               ← REMPLACER
    ├── detail_client.html     ← REMPLACER
    ├── modifie_rapport.html   ← REMPLACER
    ├── modifie_item_rapport.html ← REMPLACER
    ├── article/
    │   └── create_article.html ← REMPLACER
    └── produit/
        ├── create_produit.html     ← REMPLACER
        ├── create_rapport.html     ← REMPLACER
        └── contenu_rapport.html    ← REMPLACER
```

### 2. Remplacer le fichier form.py

Copiez `telirma/form.py` dans `facebook/telirma/form.py`.

---

## Bugs corrigés

### `form.py`

| Bug | Ligne | Avant | Après |
|-----|-------|-------|-------|
| widget incorrect | `date_de_naissance` | `widget=datetime` (module Python !) | `widget=forms.DateInput(attrs={'type':'date'})` |
| Choices dict au lieu de list | `FONCTION_CHOICES`, `SEXE_CHOICES` | `{"Inspecteur":"INSPECTEUR"}` | `[("INSPECTEUR","Inspecteur")]` |
| required string au lieu de booléen | `photo_de_profil` | `required='False'` | `required=False` |

### `templates/blog.html`

| Bug | Avant | Après |
|-----|-------|-------|
| Champ inexistant | `elts.auteurs` | `art.auteur` |

### `templates/produit/contenu_rapport.html`

| Bug | Description |
|-----|-------------|
| Balises HTML mal imbriquées | `<a>` ouverte dans un `<td>`, fermée dans le `<td>` suivant → HTML invalide |
| Corrigé | Chaque `<td>` contient ses propres boutons `<a>` correctement fermés |

### `templates/modifie_item_rapport.html` et `modifie_rapport.html`

| Bug | Avant | Après |
|-----|-------|-------|
| Pas d'`{% extends %}` | Les fichiers n'héritaient pas de `main.html` | Ajout de `{% extends 'main.html' %}` |
| Données affichées en dehors du form | Variables affichées en texte brut sans structure | Intégrées proprement dans le formulaire |

### `templates/produit/create_produit.html`

| Bug | Description |
|-----|-------------|
| Double formulaire | Contenait un formulaire produit ET un formulaire article imbriqués | Formulaire article supprimé (c'est la page produit) |

---

## Nouvelles fonctionnalités design

### Design global
- **Bootstrap 5.3** (remplace Bootstrap 4 — résout les bugs `data-toggle` / `data-dismiss`)
- **Font Awesome 6.5** pour les icônes
- **Police Exo 2** (titres) + **DM Sans** (corps)
- Palette TELIRMA : bleu marine `#0D2B5E` + bleu royal `#1558B0`

### Composants redesignés
- **Navbar** : sticky, dégradé bleu marine, badge utilisateur connecté
- **Messages** : toasts positionnés en haut à droite, disparaissent après 5s
- **Footer** : compact avec infos TELIRMA réelles
- **Cards** : ombres douces, coins arrondis, bordure colorée
- **Tables** : en-têtes bleu marine, hover coloré
- **Formulaires** : labels uppercase, focus coloré, validation inline
- **Boutons** : dégradés bleu, hover avec élévation

### Pages
| Page | Amélioration |
|------|-------------|
| `login.html` | Centré, card flottante, toggle mot de passe, lien register |
| `register.html` | Grille 2 colonnes, erreurs inline par champ |
| `home.html` | Hero banner + 4 cards services + produits récents |
| `boutique.html` | Grille responsive, images avec hover, prix mis en valeur |
| `blog.html` | Cards avec badge date, auteur corrigé |
| `crm.html` | 3 stats en haut, 2 tables séparées, boutons PDF/Edit |
| `contenu_rapport.html` | Badges statut colorés (✅ Conforme, ❌ Hors service…), formulaire ajout propre |
| `detail_client.html` | Fiche client + tableau rapports |

---

## Migration Bootstrap 4 → Bootstrap 5

Les attributs suivants ont été mis à jour :

| Bootstrap 4 | Bootstrap 5 |
|-------------|-------------|
| `data-toggle="collapse"` | `data-bs-toggle="collapse"` |
| `data-target="#..."` | `data-bs-target="#..."` |
| `data-dismiss="alert"` | `data-bs-dismiss="alert"` |
| `mr-auto` | `me-auto` |
| `ml-auto` | `ms-auto` |

---

## Modèle `Profil` — champ manquant

Dans `models.py`, le champ `function` du modèle `Profil` n'a pas de `max_length` :

```python
# ❌ AVANT — provoque une erreur de migration
function = models.CharField()

# ✅ APRÈS
function = models.CharField(max_length=50)
```

Corrigez ce point dans `telirma/models.py` puis exécutez :

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Champs extras du SignUpForm

Les champs `function`, `date_de_naissance`, `sexe`, `photo_de_profil` du formulaire d'inscription **n'appartiennent pas au modèle `User`** de Django. Pour les sauvegarder, mettez à jour la vue `register_user` :

```python
def post(self, request, *args, **kwargs):
    form = SignUpForm(request.POST, request.FILES)
    if form.is_valid():
        user = form.save()
        # Sauvegarder dans le profil
        profil = Profil.objects.create(
            user=user,
            function=form.cleaned_data['function'],
            date_de_naissance=form.cleaned_data['date_de_naissance'],
            sexe=form.cleaned_data['sexe'],
            photo_profil=form.cleaned_data.get('photo_de_profil'),
        )
        messages.success(request, "Compte créé avec succès !")
        return redirect('article:login')
```

---

*Généré pour TELIRMA — Bafoussam, Cameroun*
