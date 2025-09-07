# Form - Système de Gestion de Formulaires Multi-sites

Form est une application web complète permettant de gérer des formulaires dynamiques à travers plusieurs sous-sites. Elle offre une interface intuitive pour la création, la gestion et le suivi des formulaires, avec des fonctionnalités avancées comme la messagerie interne et le support technique.

## Fonctionnalités principales

- **Gestion Multi-sites**
  - Création et gestion de sous-sites indépendants
  - Personnalisation des thèmes par sous-site
  - Gestion des accès et des permissions

- **Formulaires Dynamiques**
  - Constructeur de formulaires intuitif
  - Types de champs variés (texte, sélection, fichiers, etc.)
  - Validation personnalisable
  - Export PDF des formulaires

- **Gestion des Utilisateurs**
  - Authentification sécurisée
  - Rôles et permissions
  - Gestion des profils

- **Communication**
  - Messagerie interne
  - Système de tickets de support
  - Notifications

## Prérequis

- Python 3.8+
- MySQL 8.0+
- Node.js 14+ (pour le développement frontend)

## Installation

1. Cloner le repository :
```bash
git clone https://github.com/votre-username/form.git
cd form
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# ou
.\venv\Scripts\activate  # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer l'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

5. Initialiser la base de données :
```bash
flask db upgrade
python -m backend.app.database.init_db
```

## Configuration

### Variables d'environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `FLASK_APP` | Point d'entrée de l'application | `run.py` |
| `FLASK_ENV` | Environnement (development/production) | `development` |
| `DATABASE_URL` | URL de connexion à la base de données | `mysql://user:pass@localhost/form` |
| `SECRET_KEY` | Clé secrète pour la session | `None` |
| `JWT_SECRET_KEY` | Clé secrète pour les tokens JWT | `None` |
| `UPLOAD_FOLDER` | Dossier pour les fichiers uploadés | `uploads` |
| `MAX_CONTENT_LENGTH` | Taille maximale des fichiers (bytes) | `16 * 1024 * 1024` |

## Structure du Projet

```
form/
├── backend/
│   ├── app/
│   │   ├── models/        # Modèles de données
│   │   ├── routes/        # Routes API
│   │   ├── database/      # Configuration base de données
│   │   └── utils/         # Utilitaires
│   └── tests/            # Tests unitaires et d'intégration
├── frontend/
│   ├── static/
│   │   ├── css/          # Styles
│   │   └── js/           # Scripts JavaScript
│   └── templates/        # Templates HTML
├── migrations/           # Migrations Alembic
├── uploads/             # Fichiers uploadés
├── .env.example         # Example de configuration
├── requirements.txt     # Dépendances Python
└── run.py              # Point d'entrée
```

## Développement

### Lancer le serveur de développement

```bash
flask run
```

### Exécuter les tests

```bash
pytest backend/tests/
```

### Créer une migration de base de données

```bash
flask db migrate -m "Description de la migration"
flask db upgrade
```

## API Documentation

L'API REST est accessible via le préfixe `/api/v1/`. La documentation complète est disponible sur `/api/docs` une fois le serveur lancé.

### Points d'entrée principaux

- `/api/v1/auth/*` - Authentification
- `/api/v1/forms/*` - Gestion des formulaires
- `/api/v1/users/*` - Gestion des utilisateurs
- `/api/v1/subsites/*` - Gestion des sous-sites
- `/api/v1/messages/*` - Messagerie
- `/api/v1/tickets/*` - Support technique

## Déploiement

### Prérequis serveur

- Serveur Linux (Ubuntu 20.04 LTS recommandé)
- Nginx
- Gunicorn
- MySQL Server
- Supervisord

### Configuration Nginx

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /chemin/vers/form/frontend/static;
    }

    location /uploads {
        alias /chemin/vers/form/uploads;
    }
}
```

### Lancement avec Gunicorn

```bash
gunicorn -w 4 -b 127.0.0.1:8000 run:app
```

### Configuration Supervisord

```ini
[program:form]
command=/chemin/vers/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 run:app
directory=/chemin/vers/form
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/form/error.log
stdout_logfile=/var/log/form/access.log
```

## Sécurité

- Toutes les routes API nécessitent une authentification par token JWT
- Les mots de passe sont hashés avec bcrypt
- Protection CSRF sur tous les formulaires
- Validation des données entrantes
- Sanitisation des données sortantes
- Limitation de taille pour les uploads
- Vérification des types MIME pour les fichiers

## Maintenance

### Sauvegarde

```bash
# Base de données
mysqldump -u user -p form > backup.sql

# Fichiers uploadés
tar -czf uploads_backup.tar.gz uploads/
```

### Mise à jour

```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
supervisorctl restart form
```

## Support

Pour toute question ou problème :

1. Consulter la documentation en ligne
2. Ouvrir un ticket via l'interface d'administration
3. Contacter le support technique

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
