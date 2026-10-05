from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('articles', '0003_article_subtitle'),
        ('problems', '0002_subject_relation'),
    ]

    operations = [
        migrations.DeleteModel(name='CodeSnippet'),
        migrations.DeleteModel(name='ArticleTag'),
        migrations.DeleteModel(name='Article'),
        migrations.DeleteModel(name='Tag'),
        migrations.DeleteModel(name='Category'),
    ]
