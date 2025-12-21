from django.core.management.base import BaseCommand

from utils.cache import view_memcached_keys


class Command(BaseCommand):
    help = "View memcached keys"

    def handle(self, *args, **options):
        view_memcached_keys()
