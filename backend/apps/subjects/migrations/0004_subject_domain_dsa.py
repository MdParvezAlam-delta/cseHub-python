from django.db import migrations, models


def rename_ds_domain_to_dsa(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    Subject.objects.filter(domain='DS').update(domain='DSA')


def rename_dsa_domain_to_ds(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    Subject.objects.filter(domain='DSA').update(domain='DS')


class Migration(migrations.Migration):
    dependencies = [
        ('subjects', '0003_subject_attribution'),
    ]

    operations = [
        migrations.RunPython(rename_ds_domain_to_dsa, rename_dsa_domain_to_ds),
        migrations.AlterField(
            model_name='subject',
            name='domain',
            field=models.CharField(
                choices=[
                    ('DSA', 'Data Structures and Algorithms'),
                    ('Web Development', 'Web Development'),
                    ('Machine Learning', 'Machine Learning'),
                    ('Systems', 'Systems'),
                    ('Programming', 'Programming'),
                ],
                default='DSA',
                max_length=80,
            ),
        ),
    ]
