from django.core.management.base import BaseCommand

from utils.cache import view_redis_keys


class Command(BaseCommand):
    help = "View redis keys"

    def add_arguments(self, parser):
        parser.add_argument(
            "--host",
            type=str,
            help="redis host",
            default="localhost",
        )

        parser.add_argument(
            "--port",
            type=int,
            help="redis port",
            default=6379,
        )

        parser.add_argument(
            "--db",
            type=int,
            help="redis db",
            default=0,
        )

    def handle(self, *args, **options):
        host = options["host"]
        port = options["port"]
        db = options["db"]

        view_redis_keys(host=host, port=port, db=db)
