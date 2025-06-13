import csv
import re
from django.core.management.base import BaseCommand
from business_intelligence.models import Movie

class Command(BaseCommand):
    help = 'Import movies from n_movies.csv into the database'

    def handle(self, *args, **kwargs):
        Movie.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted old movie data.'))

        file_path = './n_movies.csv'
        movies_to_create = []
        skipped_rows = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    year_str = row['year']
                    cleaned_year = None

                    # Coba ekstrak 4 digit angka pertama dari string tahun
                    match = re.search(r'\d{4}', year_str)
                    if match:
                        cleaned_year = int(match.group(0))
                    
                    # Cek juga nilai rating, pastikan tidak kosong
                    rating_str = row.get('rating', '0').strip()
                    if not rating_str:
                        rating = 0.0
                    else:
                        rating = float(rating_str)

                    if cleaned_year is not None:
                        movies_to_create.append(
                            Movie(
                                title=row['title'],
                                genre=row['genre'],
                                year=cleaned_year,
                                rating=rating
                            )
                        )
                    else:
                        # Lewati baris jika tahun tidak bisa diproses
                        skipped_rows += 1
                        self.stdout.write(self.style.WARNING(f"Skipping row for title '{row['title']}' due to invalid year format: '{year_str}'"))

            Movie.objects.bulk_create(movies_to_create)

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(movies_to_create)} movies.'))
            if skipped_rows > 0:
                self.stdout.write(self.style.WARNING(f'Skipped {skipped_rows} rows due to data errors.'))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Error: The file '{file_path}' was not found."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))