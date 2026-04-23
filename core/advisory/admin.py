"""
Admin configuration for the advisory app.
"""

# django_packages
from django.contrib import admin

# app_packages
from .models import AdvisoryPost


@admin.register(AdvisoryPost)
class AdvisoryPostAdmin(admin.ModelAdmin):
    """
    Admin configuration for the AdvisoryPost model.
    """

    list_display = (
        "title",
        "author",
        "post_type",
        "is_published",
        "published_at",
        "created_at",
    )
    list_filter = ("post_type", "is_published")
    search_fields = ("title", "body", "tags", "author__user__full_name")
    readonly_fields = ("published_at", "created_at")
    actions = ["publish_posts", "unpublish_posts"]

    @admin.action(description="Publish selected posts")
    def publish_posts(self, request, queryset):
        """
        Publish selected advisory posts.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request triggering the action.
        queryset : QuerySet
            The selected AdvisoryPost instances.
        """

        for post in queryset:
            post.publish()

    @admin.action(description="Unpublish selected posts")
    def unpublish_posts(self, request, queryset):
        """
        Unpublish selected advisory posts.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request triggering the action.
        queryset : QuerySet
            The selected AdvisoryPost instances.
        """

        for post in queryset:
            post.unpublish()
