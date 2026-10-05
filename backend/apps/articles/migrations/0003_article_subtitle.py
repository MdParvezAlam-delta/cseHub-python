from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('articles', '0002_article_articletag_article_tags_codesnippet')]
    operations = [
        migrations.AddField(
            model_name='article',
            name='subtitle',
            field=models.TextField(blank=True),
        ),
    ]
