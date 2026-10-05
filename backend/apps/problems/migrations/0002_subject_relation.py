import django.db.models.deletion
from django.db import migrations, models


def clear_legacy_category_links(apps, schema_editor):
    Problem = apps.get_model('problems', 'Problem')
    Problem.objects.using(schema_editor.connection.alias).update(category=None)


class Migration(migrations.Migration):
    dependencies = [
        ('problems', '0001_initial'),
        ('subjects', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(clear_legacy_category_links, migrations.RunPython.noop),
        migrations.RenameField(
            model_name='problem',
            old_name='category',
            new_name='subject',
        ),
        migrations.AlterField(
            model_name='problem',
            name='subject',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='problems',
                to='subjects.subject',
            ),
        ),
    ]
