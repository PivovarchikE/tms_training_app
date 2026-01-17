import json

from django.core.management.base import BaseCommand, CommandError

from users.tasks import send_weekly_report


class Command(BaseCommand):
    help = 'Testing celery tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['status', 'test_email', 'test_report', 'test_cleanup', 'list_scheduled'],
        )
        parser.add_argument('extra', nargs='*', help='Extra args')
        parser.add_argument('--wait', action='store_true', help='Wait for the task to complete')

    def handle(self, *args, **options):
        action = options['action']
        extra = options['extra']
        wait = options['wait']

        if action == 'status':
            self.check_status()
        elif action == 'test_email':
            self.test_email(extra, wait)
        elif action == 'test_report':
            self.test_report(wait)
        elif action == 'test_cleanup':
            self.test_cleanup(wait)
        elif action == 'list_scheduled':
            self.list_scheduled()

    def check_status(self):
        from config.celery import app

        self.stdout.write(self.style.SUCCESS('Checking RabbitMQ status ...'))

        try:
            conn = app.connection()
            conn.ensure_connection(max_retries=3)
            self.stdout.write('RabbitMQ connection established')
            conn.release()
        except Exception as exc:
            self.stdout.write('RabbitMQ connection failed')
            return

        self.stdout.write('\n Workers:')
        inspect = app.control.inspect()
        ping = inspect.ping()

        if ping:
            for worker in ping:
                self.stdout.write(f'\t{worker}')
        else:
            self.stdout.write(self.style.WARNING('No active workers found'))
            self.stdout.write('Run: celery -A config worker -l INFO')
            return

        self.stdout.write('\n Registered tasks:')
        registered = inspect.registered()
        if registered:
            for worker, tasks in registered.items():
                for task in sorted(tasks):
                    if 'users.task' in task:
                        self.stdout.write(f' * \t{task}')

    def test_email(self, extra, wait):
        from users.tasks import send_verification_email

        if not extra:
            raise CommandError('You must provide extra args. Set user_id: python manage.py celery_tasks test_email <user_id>')

        user_id = int(extra[0])

        self.stdout.write(self.style.SUCCESS(f'Sending verification email for user_id {user_id}...'))

        result = send_verification_email(user_id)

        self.stdout.write(self.style.SUCCESS('Task added to queue'))

        if wait:
            self.stdout.write('Waiting for the task to complete...')
            try:
                task_result = result.get(timeout=30)
                self.stdout.write(self.style.SUCCESS(f'\n Result:'))
                self.stdout.write(json.dumps(task_result, indent=2, ensure_ascii=False))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'\n ERROR: {exc}'))

    def test_report(self, wait):
        from users.tasks import send_weekly_report

        self.stdout.write(' Starting weekly report...')

        result = send_weekly_report.delay()

        self.stdout.write(self.style.SUCCESS(' Task added to queue'))

        if wait:
            self.stdout.write('Waiting for the task to complete...')

            try:
                task_result = result.get(timeout=60)
                self.stdout.write(self.style.SUCCESS(' \n Result:'))
                self.stdout.write(json.dumps(task_result, indent=2, ensure_ascii=False))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f' \n ERROR: {exc}'))


    def test_cleanup(self, wait):
        from users.tasks import cleanup_unverified_users

        self.stdout.write(self.style.SUCCESS('Starting cleanup tasks...'))

        result = cleanup_unverified_users.delay()

        self.stdout.write(self.style.SUCCESS('Task added to queue'))

        if wait:
            self.stdout.write('Waiting for the task to complete...')
            try:
                task_result = result.get(timeout=60)
                self.stdout.write(self.style.SUCCESS(f' \n Result:'))
                self.stdout.write(json.dumps(task_result, indent=2, ensure_ascii=False))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'\n ERROR: {exc}'))


    def list_scheduled(self):
        from django.conf import settings

        self.stdout.write('\n Scheduled tasks:')

        schedule = getattr(settings, 'CELERY_BEAT_SCHEDULE', [])

        if not schedule:
            self.stdout.write(self.style.WARNING('No scheduled tasks found'))
            return

        for name, config in schedule.items():
            task = config['task']
            scheduled_info = config['schedule']

            self.stdout.write(f'Task: \t{task}')
            self.stdout.write(f'Schedule: \t{scheduled_info}')
