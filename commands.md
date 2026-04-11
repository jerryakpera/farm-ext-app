#### Start celery

celery --app=config.celery:app worker -l INFO

<!-- Solo Worker Pool -->

celery --app=config.celery:app worker -E -l INFO --pool=solo

<!-- Start Celery beat -->

celery --app=config.celery:app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

<!-- Start flower monitoring -->

celery --app=config.celery:app flower --basic_auth=<username>:<password>
