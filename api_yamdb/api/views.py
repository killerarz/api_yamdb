from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import filters, mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.serializers import (CategoriesSerializer, CommentsSerializer, GenresSerializer, JWTTokenSerializer,
                             ReviewsSerializer, TitlesListSerializer, TitlesSerializer, UserEmailSerializer,
                             UserSerializer)
from api_yamdb.settings import ADMIN_EMAIL
from reviews.models import Categories, Genres, Reviews, Titles, User
from .permissions import IsAdministrator, IsAdministratorOrReadOnly, IsAuthorOrReadOnly, ReadOnly


class CategoriesViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    permission_classes = (IsAdministratorOrReadOnly,)


class GenresViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = GenresSerializer
    queryset = Genres.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    permission_classes = (IsAdministratorOrReadOnly,)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    filterset_class = TitleFilter
    permission_classes = (IsAdministratorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitlesSerializer
        return TitlesListSerializer

    # def get_queryset(self):
    #     return Titles.objects.all().annotate(rating=Avg('reviews__score'))


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    permission_classes = (IsAdministrator,)


class UserInfo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = User.objects.get(username=request.user.username,
                                    email=request.user.email)
        serializer = UserSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = User.objects.get(username=request.user.username,
                                email=request.user.email)

        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(role=user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUp(APIView):
    def post(self, request):
        serializer = UserEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_user, created = User.objects.get_or_create(**serializer.data)

        confirmation_code = default_token_generator.make_token(current_user)

        subject = "Confirmation code from YaMDb"
        message = f"{confirmation_code} - ваш код для авторизации на YaMDb"
        admin_email = ADMIN_EMAIL
        user_email = [current_user.email]
        send_mail(subject, message, admin_email, user_email)

        return Response(serializer.data)


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def get_queryset(self):
        title = get_object_or_404(Titles, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Titles, id=self.kwargs['title_id'])
        serializer.save(title=title, author=self.request.user)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permissions_classes = (IsAuthorOrReadOnly)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def get_queryset(self):
        review = get_object_or_404(Reviews, id=self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Reviews, id=self.kwargs['review_id'])
        serializer.save(rewiew=review, author=self.request.user)


class JWTTokenViewSet(APIView):
    def post(self, request):
        serializer = JWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_user = get_object_or_404(User, username=serializer.data["username"])
        confirmation_code = default_token_generator.make_token(current_user)
        if confirmation_code != serializer.data["confirmation_code"]:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(current_user)
        return Response({"token": str(refresh.access_token)})
