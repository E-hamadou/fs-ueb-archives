from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Projet, Commentaire, Profil
import django_filters


class InscriptionForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100, required=True, label="Prénom")
    last_name = forms.CharField(
        max_length=100, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    role = forms.ChoiceField(
        choices=[
            ('etudiant', 'Étudiant'),
            ('enseignant', 'Enseignant'),
        ],
        label="Vous êtes")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'username', 'email', 'role',
            'password1', 'password2',
            Submit('submit', "S'inscrire",
                   css_class='btn btn-ueb w-100 mt-2'),
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        role = self.cleaned_data.get('role', 'etudiant')
        profil, _ = Profil.objects.get_or_create(user=user)
        profil.role = role
        profil.save()
        return user


class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['titre', 'type_projet', 'niveau', 'filiere',
                  'encadreur', 'annee', 'resume', 'mots_cles',
                  'fichier', 'couverture', 'visibilite']
        widgets = {
            'resume': forms.Textarea(attrs={'rows': 5}),
            'mots_cles': forms.TextInput(
                attrs={'placeholder': 'Python, Django, IA, ...'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Seuls le personnel et les administrateurs peuvent restreindre
        # la visibilité d'un document ; pour les autres, ce champ est
        # retiré du formulaire et le modèle garde sa valeur par défaut
        # ('public'), quoi qu'il arrive côté client.
        peut_restreindre = user is not None and (
            user.is_staff or
            (hasattr(user, 'profil') and user.profil.role in ('personnel', 'admin'))
        )
        if not peut_restreindre:
            self.fields.pop('visibilite', None)
        else:
            self.fields['visibilite'].help_text = (
                "Un document restreint n'apparaît ni dans le catalogue, ni dans "
                "la recherche, ni au téléchargement pour les étudiants et enseignants."
            )

        self.helper = FormHelper()
        layout_fields = [
            'titre',
            Row(
                Column('type_projet', css_class='col-md-4'),
                Column('niveau', css_class='col-md-4'),
                Column('filiere', css_class='col-md-4'),
            ),
            Row(
                Column('encadreur', css_class='col-md-8'),
                Column('annee', css_class='col-md-4'),
            ),
            'resume', 'mots_cles',
            Row(
                Column('fichier', css_class='col-md-8'),
                Column('couverture', css_class='col-md-4'),
            ),
        ]
        if peut_restreindre:
            layout_fields.append('visibilite')
        layout_fields.append(
            Submit('submit', 'Soumettre le projet',
                   css_class='btn btn-success w-100 mt-3')
        )
        self.helper.layout = Layout(*layout_fields)


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu', 'note']
        widgets = {
            'contenu': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Votre avis...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Envoyer', css_class='btn btn-ueb'))


class ProfilForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=100, required=False, label="Prénom")
    last_name = forms.CharField(
        max_length=100, required=False, label="Nom")
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = Profil
        fields = ['role', 'matricule', 'filiere', 'telephone', 'photo']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        # Seulement étudiant et enseignant — admin uniquement via superuser
        self.fields['role'].choices = [
            ('etudiant', 'Étudiant'),
            ('enseignant', 'Enseignant'),
        ]
        if instance and instance.user:
            self.fields['first_name'].initial = instance.user.first_name
            self.fields['last_name'].initial = instance.user.last_name
            self.fields['email'].initial = instance.user.email
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'email',
            Row(
                Column('role', css_class='col-md-6'),
                Column('matricule', css_class='col-md-6'),
            ),
            Row(
                Column('filiere', css_class='col-md-8'),
                Column('telephone', css_class='col-md-4'),
            ),
            'photo',
            Submit('submit', 'Enregistrer',
                   css_class='btn btn-ueb w-100 mt-2'),
        )


class ProjetFilter(django_filters.FilterSet):
    titre = django_filters.CharFilter(
        lookup_expr='icontains', label='Rechercher')
    annee = django_filters.NumberFilter(label='Année')

    class Meta:
        model = Projet
        fields = ['titre', 'type_projet', 'niveau', 'filiere', 'annee']
