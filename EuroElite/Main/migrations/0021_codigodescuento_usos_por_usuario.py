from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Main", "0020_pedido_firma_entrega_pedido_foto_entrega_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="codigodescuento",
            name="usos_por_usuario",
            field=models.PositiveIntegerField(
                null=True,
                blank=True,
                help_text="Veces máximas que un mismo usuario puede usar este código",
            ),
        ),
    ]
