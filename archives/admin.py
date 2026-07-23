from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Projet, Filiere, Profil, Commentaire, Notification


class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    verbose_name_plural = 'Profil'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfilInline,)
    # Colonne rôle visible directement dans la liste des utilisateurs,
    # pratique pour repérer d'un coup d'œil qui est Personnel ou Admin.
    list_display = UserAdmin.list_display + ('get_role',)

    def get_role(self, obj):
        return obj.profil.get_role_display() if hasattr(obj, 'profil') else '—'
    get_role.short_description = 'Rôle'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    """Vue dédiée pour parcourir, filtrer et modifier les rôles en masse —
    en particulier pour assigner ou retirer le rôle Personnel sans avoir
    à ouvrir chaque utilisateur individuellement."""
    list_display = ['user', 'role', 'filiere', 'matricule', 'telephone']
    list_filter = ['role', 'filiere']
    search_fields = ['user__username', 'user__first_name',
                      'user__last_name', 'user__email', 'matricule']
    list_editable = ['role']
    autocomplete_fields = ['user']


@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code']
    search_fields = ['nom', 'code']


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'type_projet', 'niveau', 'filiere',
                     'annee', 'statut', 'visibilite', 'vues', 'date_soumission']
    list_filter = ['statut', 'visibilite', 'type_projet', 'niveau', 'filiere', 'annee']
    search_fields = ['titre', 'auteur__username', 'auteur__last_name', 'resume', 'mots_cles']
    list_editable = ['statut', 'visibilite']
    readonly_fields = ['vues', 'telechargements', 'date_soumission']
    date_hierarchy = 'date_soumission'
    actions = ['valider_projets', 'rejeter_projets']

    def valider_projets(self, request, queryset):
        queryset.update(statut='valide')
        self.message_user(request, f"{queryset.count()} projet(s) validé(s).")
    valider_projets.short_description = "Valider les projets sélectionnés"

    def rejeter_projets(self, request, queryset):
        queryset.update(statut='rejete')
        self.message_user(request, f"{queryset.count()} projet(s) rejeté(s).")
    rejeter_projets.short_description = "Rejeter les projets sélectionnés"


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ['auteur', 'projet', 'note', 'approuve', 'date']
    list_filter = ['approuve', 'note']
    list_editable = ['approuve']


admin.site.register(Notification)

admin.site.site_header = "FS-UEB Archives — Administration"
admin.site.site_title = "FS-UEB Archives"
admin.site.index_title = "Tableau de bord administrateur"
