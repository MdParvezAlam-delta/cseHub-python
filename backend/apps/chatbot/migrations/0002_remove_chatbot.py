from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('chatbot', '0001_initial'),
        ('articles', '0004_remove_legacy_articles'),
    ]
    operations = [
        migrations.DeleteModel(name='Message'),
        migrations.DeleteModel(name='Conversation'),
    ]
