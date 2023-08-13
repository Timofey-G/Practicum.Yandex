import json
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "load data from json"

    def handle(self, *args, **kwargs):
        path_to_data = Path(Path.cwd(), "data", "ingredients.json")

        with open(path_to_data) as f:
            data = json.load(f)

        for row in data:
            ingredient = Ingredient(
                name=row["name"], measurement_unit=row["measurement_unit"]
            )
            ingredient.save()
