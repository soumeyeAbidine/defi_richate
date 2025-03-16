# Generated by Django 5.0.7 on 2025-03-16 22:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('icone', models.CharField(help_text="Classe d'icône Bootstrap, ex: bi-trophy", max_length=50)),
                ('couleur', models.CharField(choices=[('primary', 'Bleu'), ('success', 'Vert'), ('warning', 'Jaune'), ('danger', 'Rouge'), ('info', 'Bleu clair'), ('dark', 'Noir')], default='primary', max_length=20)),
                ('points_requis', models.IntegerField(default=0)),
                ('mots_requis', models.IntegerField(default=0, help_text='Nombre de mots requis pour obtenir ce badge')),
                ('special', models.BooleanField(default=False, help_text='Badge spécial attribué manuellement')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Badge',
                'verbose_name_plural': 'Badges',
            },
        ),
        migrations.CreateModel(
            name='Mot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(db_index=True, max_length=60, unique=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Niveau',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('niveau', models.IntegerField(unique=True)),
                ('titre', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('points_requis', models.IntegerField()),
                ('icone', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Niveau',
                'verbose_name_plural': 'Niveaux',
                'ordering': ['niveau'],
            },
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('nom_complet', models.CharField(max_length=50)),
                ('role', models.CharField(choices=[('ADMIN', 'Administrateur'), ('MODERATEUR', 'Modérateur'), ('CONTRIBUTEUR', 'Contributeur')], default='CONTRIBUTEUR', max_length=20)),
                ('date_inscription', models.DateTimeField(auto_now_add=True)),
                ('actif', models.BooleanField(default=True)),
                ('mot_de_passe', models.CharField(default='', max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='StatutValidation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statut', models.CharField(choices=[('attente', 'En attente'), ('revision', 'En cours de révision'), ('valide', 'Validé'), ('rejete', 'Rejeté')], default='attente', max_length=10)),
                ('date_mise_a_jour', models.DateTimeField(auto_now=True)),
                ('mot', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='statut_validation', to='dictionnaire.mot')),
                ('moderateur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statuts_moderes', to='dictionnaire.utilisateur')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('lien', models.CharField(blank=True, max_length=255)),
                ('est_lue', models.BooleanField(default=False)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='dictionnaire.utilisateur')),
            ],
        ),
        migrations.AddField(
            model_name='mot',
            name='cree_par',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mots', to='dictionnaire.utilisateur'),
        ),
        migrations.CreateModel(
            name='Definition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texte', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('mot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='definitions', to='dictionnaire.mot')),
                ('ajoute_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dictionnaire.utilisateur')),
            ],
        ),
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=50)),
                ('points', models.IntegerField(default=0)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributions', to='dictionnaire.utilisateur')),
            ],
        ),
        migrations.CreateModel(
            name='Commentaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texte', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('mot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commentaires', to='dictionnaire.mot')),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionnaire.utilisateur')),
            ],
        ),
        migrations.CreateModel(
            name='BadgeUtilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_obtention', models.DateTimeField(auto_now_add=True)),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionnaire.badge')),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badges', to='dictionnaire.utilisateur')),
            ],
            options={
                'verbose_name': "Badge d'utilisateur",
                'verbose_name_plural': "Badges d'utilisateurs",
                'unique_together': {('utilisateur', 'badge')},
            },
        ),
    ]
