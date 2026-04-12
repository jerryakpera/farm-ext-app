"""
Models for `verses`.
"""

# django_packages
from django.core.validators import MinValueValidator
from django.db import models

# other_apps_packages
# local
from core.verses.choices import BibleVersionChoices


class SingleVerse(models.Model):
    """
    Atomic storage unit for a single Bible verse.
    """

    book = models.CharField(
        max_length=50,
        help_text=(
            "Bible book name exactly as used by the helloao.org API, "
            "e.g. '1John', 'Genesis', 'Psalms'."
        ),
    )
    chapter = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Chapter number within the book.",
    )
    verse = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Verse number within the chapter. Always a single verse, never a range.",
    )
    text = models.TextField(
        help_text="Full scripture text for this verse, sourced from the external Bible API.",
    )
    version = models.CharField(
        max_length=10,
        choices=BibleVersionChoices.choices,
        default=BibleVersionChoices.KJV,
        help_text="Bible translation key, e.g. 'ENGWEBP' or 'eng_kjv'.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["book", "chapter", "verse", "version"],
                name="unique_single_verse_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["book", "chapter", "verse"]),
            models.Index(fields=["version"]),
        ]
        ordering = ["book", "chapter", "verse"]
        verbose_name = "Single Verse"
        verbose_name_plural = "Single Verses"

    def __str__(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse} ({self.version})"
