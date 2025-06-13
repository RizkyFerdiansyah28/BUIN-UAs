# business_intelligence/management/commands/import_movies.py
import csv
from django.core.management.base import BaseCommand
from business_intelligence.models import Movie

class Command(BaseCommand):
    help = 'Import movies from n_movies.csv into the database'

    def handle(self, *args, **kwargs):
        # Hapus data lama untuk menghindari duplikat
        Movie.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted old movie data.'))

        # Path ke file CSV Anda
        file_path = './n_movies.csv'

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            movies_to_create = []
            for row in reader:
                movies_to_create.append(
                    Movie(
                        title=row['title'],
                        genre=row['genre'],
                        director=row['director'],
                        year=int(row['year']),
                        country=row['country']
                    )
                )

            Movie.objects.bulk_create(movies_to_create)

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(movies_to_create)} movies.'))