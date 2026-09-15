from django.db import transaction
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Product, ProductImage, ProductVideo
from .permissions import IsAdmin, IsSeller
from .serializers import (
    ProductCreateSerializer,
    ProductImageUploadSerializer,
    ProductSerializer,
    ProductVerificationSerializer,
    ProductVideoUploadSerializer,
)


class SellerProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    def get_queryset(self):
        return Product.objects.filter(
            seller=self.request.user
        ).prefetch_related(
            "images",
            "video",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductCreateSerializer

        return ProductSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        seller = self.request.user

        if not hasattr(seller, "seller_profile"):
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "Seller profile is required before creating products."
            )

        if seller.seller_profile.verification_status != "APPROVED":
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "Seller must be approved before creating products."
            )

        product = serializer.save(
            seller=seller,
            status=Product.Status.DRAFT,
        )

        self._validate_minimum_images(product)

    def _validate_minimum_images(self, product):
        image_count = product.images.count()

        if image_count < 3:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "A product must have at least 3 images."
            )


class SellerProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    serializer_class = ProductSerializer

    lookup_url_kwarg = "product_id"

    def get_queryset(self):
        return Product.objects.filter(
            seller=self.request.user
        ).prefetch_related(
            "images",
            "video",
        )

    def perform_update(self, serializer):
        product = serializer.save()

        product.status = Product.Status.DRAFT
        product.verification_note = ""
        product.save(
            update_fields=[
                "status",
                "verification_note",
                "updated_at",
            ]
        )


class ProductImageUploadView(generics.CreateAPIView):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    serializer_class = ProductImageUploadSerializer

    def perform_create(self, serializer):
        product_id = self.kwargs["product_id"]

        try:
            product = Product.objects.get(
                id=product_id,
                seller=self.request.user,
            )
        except Product.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Product not found."
            )

        serializer.save(product=product)

        if product.images.count() >= 3:
            product.status = Product.Status.PENDING
            product.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )


class SellerProductVideoView(generics.CreateAPIView):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    serializer_class = ProductVideoUploadSerializer

    def perform_create(self, serializer):
        product_id = self.kwargs["product_id"]

        try:
            product = Product.objects.get(
                id=product_id,
                seller=self.request.user,
            )
        except Product.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Product not found."
            )

        if hasattr(product, "video"):
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "This product already has a video."
            )

        serializer.save(product=product)


class SellerProductVideoDeleteView(generics.DestroyAPIView):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]

    def get_queryset(self):
        return ProductVideo.objects.filter(
            product__seller=self.request.user
        )

    lookup_url_kwarg = "video_id"


class BuyerProductListView(generics.ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.Status.APPROVED,
            seller__role="SELLER",
            seller__seller_profile__verification_status="APPROVED",
        ).prefetch_related(
            "images",
            "video",
        )


class BuyerProductDetailView(generics.RetrieveAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = ProductSerializer

    lookup_url_kwarg = "product_id"

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.Status.APPROVED,
            seller__role="SELLER",
            seller__seller_profile__verification_status="APPROVED",
        ).prefetch_related(
            "images",
            "video",
        )


class AdminProductVerificationListView(generics.ListAPIView):
    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all().select_related(
            "seller",
            "seller__seller_profile",
        ).prefetch_related(
            "images",
            "video",
        )


class AdminProductVerificationDetailView(
    generics.RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    serializer_class = ProductVerificationSerializer

    queryset = Product.objects.all()

    lookup_url_kwarg = "product_id"

    def perform_update(self, serializer):
        product = serializer.save()

        if product.status == Product.Status.APPROVED:
            if product.images.count() < 3:
                from rest_framework.exceptions import ValidationError

                raise ValidationError(
                    "Product cannot be approved without at least 3 images."
                )