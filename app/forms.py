from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Se connecter")

class RegistrationForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(3, 64)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(6, 128)])
    confirm_password = PasswordField("Confirmer le mot de passe", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("S'inscrire")

class DossierForm(FlaskForm):
    first_name = StringField("Prénom", validators=[DataRequired()])
    last_name = StringField("Nom", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    job_type = SelectField("Type de métier", choices=[
        ("metier_bouche", "Métier de bouche"),
        ("bijoux", "Bijoux"),
        ("sculpture", "Sculpture"),
        ("peinture", "Peinture"),
        ("textile", "Textile"),
        ("mode", "Mode"),
        ("autre", "Autre")
    ], validators=[DataRequired()])
    site = SelectField("Site", coerce=int)
    files = MultipleFileField("Fichiers à déposer")
    submit = SubmitField("Soumettre le dossier")

class SiteForm(FlaskForm):
    name = StringField("Nom du site", validators=[DataRequired(), Length(min=2, max=100)])
    slug = StringField("Slug du site (URL friendly)", validators=[DataRequired(), Length(min=2, max=100)])
    sub_admin_id = SelectField("Sous-admin", coerce=int, choices=[])
    submit = SubmitField("Valider")

class UserForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[Optional(), Length(min=6)])
    role = SelectField("Rôle", choices=[('super_admin', 'Super Admin'), ('sub_admin', 'Sous-admin'), ('user', 'Utilisateur')], validators=[DataRequired()])
    site_id = SelectField("Site", coerce=int, choices=[], validators=[Optional()])
    submit = SubmitField("Valider")
