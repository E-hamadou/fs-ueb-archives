from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Filiere(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Filière"
        verbose_name_plural = "Filières"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Profil(models.Model):
    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('personnel', 'Personnel (Université)'),
        ('admin', 'Administrateur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    matricule = models.CharField(max_length=50, blank=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='profils/', blank=True, null=True)

    class Meta:
        verbose_name = "Profil"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"


class Projet(models.Model):
    TYPE_CHOICES = [
        ('rapport_stage', 'Rapport de Stage'),
        ('pfe', 'Projet de Fin d\'Études'),
        ('memoire', 'Mémoire'),
        ('these', 'Thèse'),
        ('tp', 'Travail Pratique'),
        ('autre', 'Autre'),
    ]
    NIVEAU_CHOICES = [
        ('licence1', 'Licence 1'),
        ('licence2', 'Licence 2'),
        ('licence3', 'Licence 3'),
        ('master1', 'Master 1'),
        ('master2', 'Master 2'),
        ('doctorat', 'Doctorat'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente de validation'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('archive', 'Archivé'),
    ]
    VISIBILITE_CHOICES = [
        ('public', 'Public — visible par tous les utilisateurs'),
        ('restreint', 'Restreint — Personnel et Administration uniquement'),
    ]

    titre = models.CharField(max_length=300, verbose_name="Titre du projet")
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projets')
    type_projet = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name="Type")
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, verbose_name="Niveau")
    filiere = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Filière")
    encadreur = models.CharField(max_length=200, blank=True, verbose_name="Encadreur")
    annee = models.IntegerField(default=timezone.now().year, verbose_name="Année académique")
    resume = models.TextField(verbose_name="Résumé")
    mots_cles = models.CharField(max_length=500, blank=True, verbose_name="Mots-clés")
    fichier = models.FileField(upload_to='projets/%Y/%m/', verbose_name="Fichier (PDF)")
    couverture = models.ImageField(upload_to='couvertures/', blank=True, null=True, verbose_name="Image de couverture")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    visibilite = models.CharField(
        max_length=20, choices=VISIBILITE_CHOICES, default='public',
        verbose_name="Visibilité",
        help_text="Un document restreint n'est visible que par le personnel et les administrateurs."
    )
    note = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Note /20")
    vues = models.PositiveIntegerField(default=0)
    telechargements = models.PositiveIntegerField(default=0)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projet"
        ordering = ['-date_soumission']

    def __str__(self):
        return self.titre

    def get_mots_cles_list(self):
        return [m.strip() for m in self.mots_cles.split(',') if m.strip()]

    @staticmethod
    def _role_autorise_restreint(user):
        """Un utilisateur peut-il voir les documents restreints ?"""
        if not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return hasattr(user, 'profil') and user.profil.role in ('personnel', 'admin')

    def est_visible_pour(self, user):
        """Détermine si CE projet est accessible à l'utilisateur donné."""
        if self.visibilite != 'restreint':
            return True
        return Projet._role_autorise_restreint(user)

    @staticmethod
    def visibles_pour(user, queryset=None):
        """Queryset des projets validés visibles pour l'utilisateur donné.
        À utiliser partout où l'on liste ou recherche des projets, pour ne
        jamais exposer un document restreint à un étudiant ou un enseignant."""
        qs = queryset if queryset is not None else Projet.objects.all()
        qs = qs.filter(statut='valide')
        if not Projet._role_autorise_restreint(user):
            qs = qs.exclude(visibilite='restreint')
        return qs


class Commentaire(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    contenu = models.TextField(verbose_name="Commentaire")
    note = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    date = models.DateTimeField(auto_now_add=True)
    approuve = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Commentaire"
        ordering = ['-date']

    def __str__(self):
        return f"Commentaire de {self.auteur.username} sur {self.projet.titre[:50]}"


class Notification(models.Model):
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    lue = models.BooleanField(default=False)
    lien = models.CharField(max_length=300, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Notif pour {self.destinataire.username}"
