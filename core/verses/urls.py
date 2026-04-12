# third_party_packages
from rest_framework.routers import DefaultRouter

# other_apps_packages
from core.verses.views import MemoryVerseViewSet


router = DefaultRouter()
router.register(r"verses", MemoryVerseViewSet, basename="verses")

urlpatterns = router.urls
