"""
Models for the advisory app.
"""

# django_packages
from django.db import models
from django.utils import timezone

# third_party_packages
from taggit.managers import TaggableManager

# other_apps_packages
from core.profiles.models import ExtensionAgentProfile


class AdvisoryPost(models.Model):
    """
    An advisory post created by an extension agent to share farming tips,
    instructional articles, videos, or infographics with farmers.
    """

    class PostType(models.TextChoices):
        """
        Choice lists for the post types.
        """

        ARTICLE = "article", "Article"
        VIDEO = "video", "Video"
        INFOGRAPHIC = "infographic", "Infographic"
        OTHER = "other", "Other"

    author = models.ForeignKey(
        ExtensionAgentProfile,
        on_delete=models.CASCADE,
        related_name="advisory_posts",
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    post_type = models.CharField(
        max_length=20,
        choices=PostType.choices,
        default=PostType.ARTICLE,
    )
    video_url = models.URLField(
        blank=True,
        help_text="Optional link to an embedded video, e.g. a YouTube or Vimeo URL.",
    )
    attachment = models.FileField(
        upload_to="advisory_attachments/",
        null=True,
        blank=True,
        help_text="Optional file upload such as a PDF guide or data sheet.",
    )
    cover_image = models.ImageField(
        upload_to="advisory_covers/",
        null=True,
        blank=True,
    )
    tags = TaggableManager(blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set automatically when the post is first published.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Advisory Post"
        verbose_name_plural = "Advisory Posts"
        ordering = ["-created_at"]

    def __str__(self):
        """
        Return the string representation of an advisory post.

        Returns
        -------
        str
            The post title and author full name.
        """

        return f"{self.title} — {self.author.user.full_name}"

    def publish(self):
        """
        Publish the advisory post and set the publication timestamp if it is the first publication.
        """

        if not self.is_published:
            self.published_at = timezone.now()

        self.is_published = True
        self.save(update_fields=["is_published", "published_at"])

    def unpublish(self):
        """
        Unpublish the post, hiding it from farmers.
        """

        self.is_published = False
        self.save(update_fields=["is_published"])
