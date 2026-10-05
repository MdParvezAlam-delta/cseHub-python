from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('subjects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='domain',
            field=models.CharField(
                choices=[
                    ('DS', 'Data Science'),
                    ('Web Development', 'Web Development'),
                    ('Machine Learning', 'Machine Learning'),
                    ('Systems', 'Systems'),
                    ('Programming', 'Programming'),
                ],
                default='DS',
                max_length=80,
            ),
        ),
        migrations.AddField(
            model_name='subject',
            name='module_heading',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='subject',
            name='content_markdown',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='subject',
            name='code_snippets',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='subject',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
