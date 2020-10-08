from django.contrib import admin
from webapp.models import Article, Comment, Tag, ArticleLike


class ArticleAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)


admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(ArticleLike)
