# third_party_packages
from rest_framework.routers import DefaultRouter

# other_apps_packages
from core.verses.views import MemoryVerseViewSet, TopicViewSet, UserVerseViewSet


router = DefaultRouter()

router.register(r"memory-verses", MemoryVerseViewSet, basename="verses")
router.register(r"user-verses", UserVerseViewSet, basename="user-verse")
router.register(r"topics", TopicViewSet, basename="topic")

urlpatterns = router.urls
