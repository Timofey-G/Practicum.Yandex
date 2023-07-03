import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title, User


class Command(BaseCommand):
    help = "load data from csv"

    def handle(self, *args, **kwargs):
        path_to_data = Path(Path.cwd(), "static", "data")

        path_to_users = Path(path_to_data, "users.csv")
        path_to_genre = Path(path_to_data, "genre.csv")
        path_to_category = Path(path_to_data, "category.csv")
        path_to_titles = Path(path_to_data, "titles.csv")
        path_to_genre_titles = Path(path_to_data, "genre_title.csv")
        path_to_review = Path(path_to_data, "review.csv")
        path_to_comments = Path(path_to_data, "comments.csv")

        with open(path_to_users, encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                id = row["id"]
                username = row["username"]
                email = row["email"]
                role = row["role"]
                bio = row["bio"]
                first_name = row["first_name"]
                last_name = row["last_name"]
                user = User(
                    id=id,
                    username=username,
                    email=email,
                    role=role,
                    bio=bio,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.save()

        with open(path_to_genre, encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                id = row["id"]
                name = row["name"]
                slug = row["slug"]
                genre = Genre(id=id, name=name, slug=slug)
                genre.save()

        with open(path_to_category, encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                id = row["id"]
                name = row["name"]
                slug = row["slug"]
                category = Category(id=id, name=name, slug=slug)
                category.save()

        with open(path_to_titles, encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                id = row["id"]
                name = row["name"]
                year = row["year"]
                category_id = row["category"]
                category = Category.objects.get(id=category_id)
                title = Title(id=id, name=name, year=year, category=category)
                title.save()

        with open(path_to_genre_titles, encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                title_id = row["title_id"]
                title = Title.objects.get(id=title_id)
                genre_id = row["genre_id"]
                genre = Genre.objects.get(id=genre_id)
                title.genre.add(genre)

        with open(path_to_review, encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                id = row["id"]
                title_id = row["title_id"]
                title = Title.objects.get(id=title_id)
                text = row["text"]
                author_id = row["author"]
                author = User.objects.get(id=author_id)
                score = row["score"]
                pub_date = row["pub_date"]
                review = Review(
                    id=id,
                    title=title,
                    text=text,
                    author=author,
                    score=score,
                    pub_date=pub_date,
                )
                review.save()

        with open(path_to_comments, encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                id = row["id"]
                review_id = row["review_id"]
                review = Review.objects.get(id=review_id)
                text = row["text"]
                author_id = row["author"]
                author = User.objects.get(id=author_id)
                pub_date = row["pub_date"]
                comments = Comment(
                    id=id,
                    review=review,
                    text=text,
                    author=author,
                    pub_date=pub_date,
                )
                comments.save()
