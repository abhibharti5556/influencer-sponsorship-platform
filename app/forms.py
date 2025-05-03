from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    TextAreaField,
    FloatField,
    DateField,
    SelectField,
    DecimalField,
    URLField,
    IntegerField,
)
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, URL, Optional


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")


class CampaignForm(FlaskForm):
    name = StringField("Campaign Name", validators=[DataRequired(), Length(max=100)])
    title = StringField("Campaign Title", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[DataRequired()])
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    duration = IntegerField("Duration (Days)", validators=[Optional(), NumberRange(min=1)])
    budget = FloatField("Budget", validators=[DataRequired(), NumberRange(min=0)])
    platform = SelectField(
        "Platform",
        choices=[
            ("instagram", "Instagram"),
            ("youtube", "YouTube"),
            ("tiktok", "TikTok"),
            ("twitter", "Twitter"),
            ("facebook", "Facebook"),
            ("twitch", "Twitch"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    requirements = TextAreaField("Requirements", validators=[Optional()])
    niche = SelectField(
        "Niche",
        choices=[
            ("technology", "Technology"),
            ("fashion", "Fashion"),
            ("food", "Food"),
            ("travel", "Travel"),
            ("fitness", "Fitness"),
            ("beauty", "Beauty"),
            ("gaming", "Gaming"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    status = SelectField(
        "Status", 
        choices=[
            ("active", "Active"),
            ("pending", "Pending"),
            ("inactive", "Inactive")
        ],
        default="active"
    )
    visibility = SelectField(
        "Visibility", choices=[("public", "Public"), ("private", "Private")]
    )


class InfluencerSearchForm(FlaskForm):
    niche = SelectField(
        "Niche",
        choices=[
            ("technology", "Technology"),
            ("fashion", "Fashion"),
            ("food", "Food"),
            ("travel", "Travel"),
            ("fitness", "Fitness"),
            ("beauty", "Beauty"),
            ("gaming", "Gaming"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Search")


class AdRequestForm(FlaskForm):
    requirements = TextAreaField("Requirements", validators=[DataRequired()])
    payment_amount = DecimalField(
        "Payment Amount", validators=[DataRequired(), NumberRange(min=0)]
    )
    submit = SubmitField("Send Ad Request")


class CampaignSearchForm(FlaskForm):
    niche = SelectField(
        "Niche",
        choices=[
            ("technology", "Technology"),
            ("fashion", "Fashion"),
            ("food", "Food"),
            ("travel", "Travel"),
            ("fitness", "Fitness"),
            ("beauty", "Beauty"),
            ("gaming", "Gaming"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Search")


class InfluencerProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    profile_picture = FileField("Profile Picture", validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=500)])
    category = StringField("Category", validators=[DataRequired()])
    niche = SelectField(
        "Niche",
        choices=[
            ("technology", "Technology"),
            ("fashion", "Fashion"),
            ("food", "Food"),
            ("travel", "Travel"),
            ("fitness", "Fitness"),
            ("beauty", "Beauty"),
            ("gaming", "Gaming"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    instagram = URLField("Instagram URL", validators=[Optional(), URL()])
    twitter = URLField("Twitter URL", validators=[Optional(), URL()])
    youtube = URLField("YouTube URL", validators=[Optional(), URL()])
    tiktok = URLField("TikTok URL", validators=[Optional(), URL()])
    website = URLField("Website URL", validators=[Optional(), URL()])
    followers_count = IntegerField("Followers Count", validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField("Update Profile")


class SponsorProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    profile_picture = FileField("Profile Picture", validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    email = StringField("Email", validators=[DataRequired(), Email()])
    company = StringField("Company", validators=[Optional()])
    bio = TextAreaField("About Your Company", validators=[Optional(), Length(max=500)])
    website = URLField("Website URL", validators=[Optional(), URL()])
    instagram = URLField("Instagram URL", validators=[Optional(), URL()])
    twitter = URLField("Twitter URL", validators=[Optional(), URL()])
    submit = SubmitField("Update Profile")


class AdminProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    profile_picture = FileField("Profile Picture", validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    email = StringField("Email", validators=[DataRequired(), Email()])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=500)])
    website = URLField("Website URL", validators=[Optional(), URL()])
    submit = SubmitField("Update Profile")


class AdminCampaignSearchForm(FlaskForm):
    niche = SelectField(
        "Niche",
        choices=[
            ("", "All Niches"),
            ("technology", "Technology"),
            ("fashion", "Fashion"),
            ("food", "Food"),
            ("travel", "Travel"),
            ("fitness", "Fitness"),
            ("beauty", "Beauty"),
            ("gaming", "Gaming"),
            ("other", "Other"),
        ],
        validators=[Optional()],
    )
    submit = SubmitField("Search")


class AdminUserSearchForm(FlaskForm):
    role = SelectField(
        "Role",
        choices=[
            ("", "All Roles"),
            ("influencer", "Influencers"),
            ("sponsor", "Sponsors"),
            ("admin", "Admins"),
        ],
        validators=[Optional()],
    )
    submit = SubmitField("Search")
