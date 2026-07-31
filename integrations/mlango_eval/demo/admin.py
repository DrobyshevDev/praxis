"""Admin: golden set виден в mlango-admin для просмотра кейсов."""

from mlango import admin

from demo.datasets import GoldenCases


@admin.register(GoldenCases)
class GoldenCasesAdmin(admin.ObjectAdmin):
    list_display = ("id", "question", "expected")
    search_fields = ("question",)
    list_per_page = 25
