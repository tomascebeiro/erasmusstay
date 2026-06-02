from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("housing", "0002_alter_anuncio_options_alter_imagenanuncio_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="imagenanuncio",
            name="imagen",
            field=models.ImageField(blank=True, null=True, upload_to="anuncios/%Y/%m/%d/"),
        ),
        migrations.AddField(
            model_name="valoracion",
            name="aprobado",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="SolicitudContacto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mensaje", models.TextField(blank=True)),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("pendiente", "Pendiente"),
                            ("respondida", "Respondida"),
                            ("cerrada", "Cerrada"),
                        ],
                        default="pendiente",
                        max_length=20,
                    ),
                ),
                ("telefono_propietario_snapshot", models.CharField(blank=True, max_length=20)),
                ("email_propietario_snapshot", models.EmailField(blank=True, max_length=254)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
                (
                    "anuncio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solicitudes_contacto",
                        to="housing.anuncio",
                    ),
                ),
                (
                    "estudiante",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solicitudes_realizadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Solicitud de contacto",
                "verbose_name_plural": "Solicitudes de contacto",
                "ordering": ["-fecha_creacion"],
            },
        ),
    ]