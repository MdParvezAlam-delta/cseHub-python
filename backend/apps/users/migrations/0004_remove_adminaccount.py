from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_adminaccount'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AdminAccount',
        ),
    ]
