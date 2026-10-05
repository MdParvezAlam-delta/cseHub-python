import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('subjects', '0002_subject_authoring_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='author',
            field=models.CharField(default='CSEHub Admin', max_length=100),
        ),
        migrations.AddField(
            model_name='subject',
            name='publish_date',
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
        migrations.RemoveField(
            model_name='subject',
            name='module_heading',
        ),
    ]
