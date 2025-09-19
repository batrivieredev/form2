"""
app/forms.py
Formulaires Flask-WTF pour authentification, inscription et dépôt de dossier.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# =============================
# Formulaire de Connexion
# =============================
class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Connexion")


# =============================
# Formulaire d'Inscription utilisateur
# =============================
class RegistrationForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField("Confirmer mot de passe", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("S'inscrire")


# =============================
# Formulaire de dépôt de dossier (questionnaire + fichiers)
# =============================
class DossierForm(FlaskForm):
    prenom = StringField("Prénom", validators=[DataRequired()])
    nom = StringField("Nom", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    telephone = StringField("Téléphone", validators=[DataRequired()])

    # Choix métier
    metier = SelectField(
        "Type de métier",
        choices=[
            ("metiers_bouche", "Métiers de bouche"),
            ("bijoux", "Bijoux"),
            ("sculpture", "Sculpture"),
            ("textile", "Textile"),
            ("cuir", "Cuir"),
            ("bois", "Bois"),
            ("verre", "Verre"),
            ("poterie", "Poterie"),
            ("peinture", "Peinture"),
            ("photographie", "Photographie"),
            ("cosmetique", "Cosmétique"),
            ("decoration", "Décoration"),
            ("autre", "Autre")
        ],
        validators=[DataRequired()]
    )

    fichier = FileField("Déposer vos fichiers (PDF, DOCX, images)", validators=[DataRequired()])
    submit = SubmitField("Soumettre le dossier")


# =============================
# Formulaire de messagerie
# =============================
class MessageForm(FlaskForm):
    body = TextAreaField("Message", validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField("Envoyer")
