from rest_framework import serializers

from .models import Subject


class CodeSnippetSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=['JavaScript', 'Python', 'Java', 'C++'])
    code = serializers.CharField(allow_blank=True)


class SubjectSerializer(serializers.ModelSerializer):
    code_snippets = CodeSnippetSerializer(many=True, required=False)

    class Meta:
        model = Subject
        fields = [
            'id',
            'name',
            'author',
            'publish_date',
            'description',
            'icon',
            'domain',
            'content_markdown',
            'code_snippets',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
