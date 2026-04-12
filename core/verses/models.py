"""
Models for `verses`.
"""

# django_packages
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

# other_apps_packages
# apps_packages
from core.verses.choices import BibleVersionChoices


class Topic(models.Model):
    """
    A thematic classification that can be applied to :class:`MemoryVerse`
    records.
    """

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Topic"
        verbose_name_plural = "Topics"

    def __str__(self) -> str:
        """
        Returns the str representation of the model.

        Returns
        -------
        str
            Representation of the topic instance.
        """

        return self.name


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


class MemoryVerse(models.Model):
    """
    A user-facing scripture selection — one verse or a consecutive range of
    up to three verses.
    """

    verse_start = models.ForeignKey(
        SingleVerse,
        on_delete=models.PROTECT,
        related_name="memory_verses_as_start",
        help_text="The first (or only) verse of this selection.",
    )
    verse_end = models.ForeignKey(
        SingleVerse,
        on_delete=models.PROTECT,
        related_name="memory_verses_as_end",
        null=True,
        blank=True,
        help_text=(
            "The last verse of this selection. "
            "Null when the selection is a single verse."
        ),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_memory_verses",
        help_text="The user who first added this selection to the database.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["verse_start", "verse_end"],
                name="unique_memory_verse_selection",
            ),
        ]
        ordering = ["verse_start__book", "verse_start__chapter", "verse_start__verse"]
        verbose_name = "Memory Verse"
        verbose_name_plural = "Memory Verses"

    @property
    def version(self) -> str:
        """
        Return the Bible translation key for this selection.

        Returns
        -------
        str
            The Bible version identifier (e.g. "eng_kjv").
        """

        return self.verse_start.version

    @property
    def reference(self) -> str:
        """
        Return a human-readable scripture reference string.

        Returns
        -------
        str
            A formatted scripture reference such as "Genesis 1:1" or "Genesis 1:1-3".
        """

        book = self.verse_start.book
        chapter = self.verse_start.chapter
        start = self.verse_start.verse

        if self.verse_end is None:
            return f"{book} {chapter}:{start}"

        return f"{book} {chapter}:{start}-{self.verse_end.verse}"

    @property
    def display_text(self) -> str:
        """
        Return the full scripture text for this selection.

        Returns
        -------
        str
            The scripture of the verse.
        """

        if self.verse_end is None:
            return self.verse_start.text

        verses = (
            SingleVerse.objects.filter(
                book=self.verse_start.book,
                chapter=self.verse_start.chapter,
                version=self.verse_start.version,
                verse__gte=self.verse_start.verse,
                verse__lte=self.verse_end.verse,
            )
            .order_by("verse")
            .values_list("text", flat=True)
        )

        return " ".join(verses)

    def __str__(self) -> str:
        """
        Return the str representation of the model.

        Returns
        -------
        str
            Str representation of the model.
        """

        return f"{self.reference}"
