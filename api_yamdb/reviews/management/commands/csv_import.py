from csv import DictReader
from django.core.management import BaseCommand

# Import the model
from reviews.models import Categories, Genres, Titles, GenreTitles

class Command(BaseCommand):
    def handle(self, *args, **options):

        # Show this if the data already exist in the database
        if Categories.objects.exists():
            Categories.objects.all().delete()

        print("Import Categories")
        for row in DictReader(open('./static/data/category.csv')):
            category = Categories(id=row['id'], name=row['name'], slug=row['slug'])
            category.save()
        print("Import Categories done")

        if Genres.objects.exists():
            Genres.objects.all().delete()

        print("Import Genres")
        for row in DictReader(open('./static/data/genre.csv')):
            genre = Genres(id=row['id'], name=row['name'], slug=row['slug'])
            genre.save()
        print("Import Genres done")

        if Titles.objects.exists():
            Titles.objects.all().delete()

        print("Import Titles")
        for row in DictReader(open('./static/data/titles.csv')):
            category = Categories.objects.get(id=row['category'])
            title = Titles(id=row['id'], name=row['name'], year=row['year'], category=category)
            title.save()
        print("Import Titles done")

        print("Import Genre_Title")
        for row in DictReader(open('./static/data/genre_title.csv')):
            title = Titles.objects.get(id=row['title_id'])
            genre = Genres.objects.get(id=row['genre_id'])
            genretitle = GenreTitles(id=row['id'], title=title, genre=genre)
            genretitle.save()
        print("Import Genre_Title done")