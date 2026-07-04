from django.contrib import admin
from django.utils.html import format_html

from .models import Paper, Question


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ('board', 'class_name', 'subject', 'year')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'subject', 'board', 'year', 'has_image')
    list_filter = ('board', 'subject', 'chapter')
    search_fields = ('question_text', 'chapter')
    readonly_fields = ('image_preview',)

    @admin.display(boolean=True, description='Has image')
    def has_image(self, obj):
        return bool(obj.question_image)

    @admin.display(description='Image preview')
    def image_preview(self, obj):
        if obj.question_image:
            return format_html(
                '<img src="{}" style="max-width:480px;border-radius:8px;border:1px solid #ccc;" />',
                obj.question_image.url,
            )
        return '—'
