import os
from csv import DictReader

from django.core.management import BaseCommand

from api_yamdb.settings import BASE_DIR
from reviews.models import Categories, GenreTitles, Genres, Titles, User, Reviews, Comments

MODEL_FILE = {
    Categories: "category.csv",
    Genres: "genre.csv",
    Titles: "titles.csv",
    User: "users.csv",
    GenreTitles: "genre_title.csv",
    Reviews: "review.csv",
    Comments: "comments.csv"
}


class Command(BaseCommand):
    def import_data(self, Model, fileName: str):
        print(f"Import model {Model.__name__}")
        if Model.objects.exists():
            Model.objects.all().delete()

        path = os.path.join(BASE_DIR, "static/data", fileName)
        reader = list(DictReader(open(path, encoding="utf8")))

        for dct in map(dict, reader):
            if Model.__name__ == "Titles":
                category = Categories.objects.get(id=dct.pop("category"))
                Model.objects.create(**dct, category=category)

            elif Model.__name__ == "GenreTitles":
                title = Titles.objects.get(id=dct.pop("title_id"))
                genre = Genres.objects.get(id=dct.pop("genre_id"))
                Model.objects.create(**dct, title=title, genre=genre)

            elif Model.__name__== "Reviews":
                title = Titles.objects.get(id=dct.pop("title_id"))
                author = User.objects.get(id=dct.pop("author"))
                Model.objects.create(**dct, title=title, author=author)

            elif Model.__name__== "Comments":
                review = Reviews.objects.get(id=dct.pop("review_id"))
                author = User.objects.get(id=dct.pop("author"))
                Model.objects.create(**dct, review=review, author=author)

            else:
                Model.objects.create(**dct)
        print(f"Import model {Model.__name__} done")

    def handle(self, *args, **options):
        for model, filename in MODEL_FILE.items():
            self.import_data(model, filename)
