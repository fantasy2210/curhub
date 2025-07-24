import json
from django.core.management.base import BaseCommand
from django.core import serializers

class Command(BaseCommand):
    help = 'Dumps data to a JSON file with UTF-8 encoding'

    def handle(self, *args, **options):
        from django.apps import apps
        app_models = apps.get_models()
        all_objects = []
        for model in app_models:
            all_objects.extend(model.objects.all())

        data = serializers.serialize("json", all_objects, indent=4)
        with open('data.json', 'w', encoding='utf-8') as f:
            f.write(data)
        self.stdout.write(self.style.SUCCESS('Successfully dumped data to data.json'))