from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order

from .models import ReturnRequest, ReturnProof
from .serializers import (
    ReturnRequestSerializer,
    ReturnProofSerializer,
    CustomerUPIRefundSerializer,
    ReturnReviewSerializer,
    ReturnStatusSerializer,
    RefundStatusSerializer,
)


# =========================================================
# CUSTOMER RETURN CREATE
# =========================================================

class CustomerReturnListCreateView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        returns = ReturnRequest.objects.filter(
            customer=request.user
        ).select_related(
            "order",
            "order_item",
        ).prefetch_related(
            "proofs"
        )

        serializer = ReturnRequestSerializer(
            returns,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = ReturnRequestSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True
        )

        return_request = serializer.save()

        # Automatically run fraud/risk checks.
        calculate_return_risk(return_request)

        return Response(
            ReturnRequestSerializer(
                return_request,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# CUSTOMER RETURN DETAIL
# =========================================================

class CustomerReturnDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(self, request, return_id):

        return ReturnRequest.objects.filter(
            id=return_id,
            customer=request.user,
        ).select_related(
            "order",
            "order_item",
        ).prefetch_related(
            "proofs"
        ).first()

    def get(self, request, return_id):

        return_request = self.get_object(
            request,
            return_id
        )

        if not return_request:
            return Response(
                {"detail": "Return request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReturnRequestSerializer(
            return_request,
            context={"request": request},
        )

        return Response(serializer.data)


# =========================================================
# CUSTOMER UPLOAD RETURN PROOF
# =========================================================

class ReturnProofCreateView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request, return_id):

        return_request = ReturnRequest.objects.filter(
            id=return_id,
            customer=request.user,
        ).first()

        if not return_request:
            return Response(
                {"detail": "Return request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if return_request.status in [
            ReturnRequest.Status.REJECTED,
            ReturnRequest.Status.CANCELLED,
            ReturnRequest.Status.COMPLETED,
        ]:
            return Response(
                {
                    "detail": (
                        "Proof cannot be uploaded for "
                        "this return status."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        image = request.FILES.get("image")

        if not image:
            return Response(
                {"detail": "Image is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 5 MB limit
        if image.size > 5 * 1024 * 1024:
            return Response(
                {
                    "detail": (
                        "Image size must be less than 5 MB."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        ]

        filename = image.name.lower()

        if not any(
            filename.endswith(ext)
            for ext in allowed_extensions
        ):
            return Response(
                {
                    "detail": (
                        "Only JPG, JPEG, PNG and WEBP "
                        "images are allowed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReturnProofSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        proof = ReturnProof.objects.create(
            return_request=return_request,
            proof_type=request.data.get(
                "proof_type"
            ),
            image=image,
            latitude=request.data.get(
                "latitude"
            ) or None,
            longitude=request.data.get(
                "longitude"
            ) or None,
            note=request.data.get(
                "note",
                "",
            ),
        )

        # Recalculate risk after proof upload.
        calculate_return_risk(return_request)

        return Response(
            ReturnProofSerializer(proof).data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# CUSTOMER ADD / UPDATE UPI ID
# =========================================================

class CustomerUPIRefundView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, return_id):

        return_request = ReturnRequest.objects.filter(
            id=return_id,
            customer=request.user,
        ).first()

        if not return_request:
            return Response(
                {"detail": "Return request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CustomerUPIRefundSerializer(
            return_request,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return_request.refund_amount = (
            return_request.calculate_refund_amount()
        )

        return_request.save(
            update_fields=[
                "refund_amount",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "UPI ID saved successfully.",
                "refund_amount": str(
                    return_request.refund_amount
                ),
                "refund_status": (
                    return_request.refund_status
                ),
            }
        )


# =========================================================
# SELLER RETURN LIST
# =========================================================

class SellerReturnListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        if request.user.role != "SELLER":
            return Response(
                {"detail": "Seller access required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        returns = ReturnRequest.objects.filter(
            order_item__seller=request.user
        ).select_related(
            "order",
            "order_item",
            "customer",
        ).prefetch_related(
            "proofs"
        )

        serializer = ReturnRequestSerializer(
            returns,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)


# =========================================================
# ADMIN RETURN LIST
# =========================================================

class AdminReturnListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        if (
            request.user.role != "ADMIN"
            or not request.user.is_staff
        ):
            return Response(
                {"detail": "Admin access required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        returns = ReturnRequest.objects.all().select_related(
            "order",
            "order_item",
            "customer",
        ).prefetch_related(
            "proofs"
        )

        serializer = ReturnRequestSerializer(
            returns,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)


# =========================================================
# ADMIN REVIEW
# =========================================================

class AdminReturnReviewView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def patch(self, request, return_id):

        if (
            request.user.role != "ADMIN"
            or not request.user.is_staff
        ):
            return Response(
                {"detail": "Admin access required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return_request = ReturnRequest.objects.select_for_update().filter(
            id=return_id
        ).first()

        if not return_request:
            return Response(
                {"detail": "Return request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReturnReviewSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        action = serializer.validated_data["action"]

        admin_note = serializer.validated_data.get(
            "admin_note",
            "",
        )

        suspicious_reason = serializer.validated_data.get(
            "suspicious_reason",
            "",
        )

        # -----------------------------------------
        # APPROVE
        # -----------------------------------------

        if action == "APPROVE":

            return_request.status = (
                ReturnRequest.Status.APPROVED
            )

            return_request.suspicious = False
            return_request.suspicious_reviewed = True

            return_request.admin_note = admin_note

            return_request.approved_at = timezone.now()

            return_request.refund_status = (
                ReturnRequest.RefundStatus.PENDING
            )

            return_request.save()

        # -----------------------------------------
        # REJECT
        # -----------------------------------------

        elif action == "REJECT":

            return_request.status = (
                ReturnRequest.Status.REJECTED
            )

            return_request.suspicious_reviewed = True
            return_request.admin_note = admin_note

            return_request.refund_status = (
                ReturnRequest.RefundStatus.REJECTED
            )

            return_request.save()

        # -----------------------------------------
        # SUSPICIOUS
        # -----------------------------------------

        elif action == "SUSPICIOUS":

            return_request.status = (
                ReturnRequest.Status.SUSPICIOUS
            )

            return_request.suspicious = True
            return_request.suspicious_reviewed = False

            if suspicious_reason:
                reasons = return_request.suspicious_reasons or []

                if suspicious_reason not in reasons:
                    reasons.append(suspicious_reason)

                return_request.suspicious_reasons = reasons

            return_request.admin_note = admin_note

            return_request.save()

        return Response(
            ReturnRequestSerializer(
                return_request,
                context={"request": request},
            ).data
        )


# =========================================================
# ADMIN RETURN STATUS
# =========================================================

class AdminReturnStatusView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def patch(self, request, return_id):

        if (
            request.user.role != "ADMIN"
            or not request.user.is_staff
        ):
            return Response(
                {"detail": "Admin access required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return_request = ReturnRequest.objects.select_for_update().filter(
            id=return_id
        ).first()

        if not return_request:
            return Response(
                {"detail": "Return request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReturnStatusSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        new_status = serializer.validated_data[
            "status"
        ]

        admin_note = serializer.validated_data.get(
            "admin_note",
            "",
        )

        # Suspicious return cannot directly move ahead.
        if (
            return_request.status
            == ReturnRequest.Status.SUSPICIOUS
        ):
            return Response(
                {
                    "detail": (
                        "Suspicious return must be "
                        "reviewed before status update."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------
        # PICKUP ASSIGNED
        # -----------------------------------------

        if new_status == ReturnRequest.Status.PICKUP_ASSIGNED:

            if return_request.status != ReturnRequest.Status.APPROVED:
                return Response(
                    {
                        "detail": (
                            "Return must be approved "
                            "before pickup assignment."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # -----------------------------------------
        # PICKED UP
        # -----------------------------------------

        elif new_status == ReturnRequest.Status.PICKED_UP:

            if (
                return_request.status
                != ReturnRequest.Status.PICKUP_ASSIGNED
            ):
                return Response(
                    {
                        "detail": (
                            "Return must be pickup assigned "
                            "before pickup."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return_request.picked_up_at = timezone.now()

        # -----------------------------------------
        # RECEIVED
        # -----------------------------------------

        elif new_status == ReturnRequest.Status.RECEIVED:

            if (
                return_request.status
                != ReturnRequest.Status.PICKED_UP
            ):
                return Response(
                    {
                        "detail": (
                            "Return must be picked up "
                            "before received."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return_request.received_at = timezone.now()

        # -----------------------------------------
        # COMPLETED
        # -----------------------------------------

        elif new_status == ReturnRequest.Status.COMPLETED:

            if (
                return_request.status
                != ReturnRequest.Status.RECEIVED
            ):
                return Response(
                    {
                        "detail": (
                            "Return must be received "
                            "before completion."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if return_request.refund_status != (
                ReturnRequest.RefundStatus.COMPLETED
            ):
                return Response(
                    {
                        "detail": (
                            "Refund must be completed "
                            "before completing the return."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return_request.completed_at = timezone.now()

        # -----------------------------------------
        # CANCELLED
        # -----------------------------------------

        elif new_status == ReturnRequest.Status.CANCELLED:

            if return_request.status in [
                ReturnRequest.Status.COMPLETED,
                ReturnRequest.Status.RECEIVED,
            ]:
                return Response(
                    {
                        "detail": (
                            "This return cannot be cancelled now."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return_request.status = new_status

        if admin_note:
            return_request.admin_note = admin_note

        return_request.save()

        return Response(
            ReturnRequestSerializer(
                return_request,
                context={"request": request},
            ).data
        )


# =========================================================
# ADMIN REFUND STATUS
# =========================================================

class AdminRefundStatusView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def patch(self, request, return_id):

        if (
            request.user.role != "ADMIN"
            or not request.user.is_staff
        ):
            return Response(
                {"detail": "Admin access required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return_request = ReturnRequest.objects.select_for_update().filter(
            id=return_id
        ).first()

        if not return_request:
            return Response(
                {"detail": "Return request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RefundStatusSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        new_status = serializer.validated_data[
            "status"
        ]

        transaction_id = serializer.validated_data.get(
            "transaction_id",
            "",
        )

        refund_note = serializer.validated_data.get(
            "refund_note",
            "",
        )

        # Refund cannot happen for suspicious return.
        if return_request.status == (
            ReturnRequest.Status.SUSPICIOUS
        ):
            return Response(
                {
                    "detail": (
                        "Refund is blocked because "
                        "this return is suspicious."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # UPI ID required for refund processing.
        if new_status in [
            ReturnRequest.RefundStatus.APPROVED,
            ReturnRequest.RefundStatus.PROCESSING,
            ReturnRequest.RefundStatus.COMPLETED,
        ]:

            if not return_request.refund_upi_id:
                return Response(
                    {
                        "detail": (
                            "Customer UPI ID is required "
                            "before refund processing."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # -----------------------------------------
        # APPROVED
        # -----------------------------------------

        if new_status == (
            ReturnRequest.RefundStatus.APPROVED
        ):

            if return_request.status not in [
                ReturnRequest.Status.APPROVED,
                ReturnRequest.Status.PICKUP_ASSIGNED,
                ReturnRequest.Status.PICKED_UP,
                ReturnRequest.Status.RECEIVED,
            ]:
                return Response(
                    {
                        "detail": (
                            "Return must be approved "
                            "before refund approval."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # -----------------------------------------
        # PROCESSING
        # -----------------------------------------

        elif new_status == (
            ReturnRequest.RefundStatus.PROCESSING
        ):

            if return_request.refund_status != (
                ReturnRequest.RefundStatus.APPROVED
            ):
                return Response(
                    {
                        "detail": (
                            "Refund must first be approved."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # -----------------------------------------
        # COMPLETED
        # -----------------------------------------

        elif new_status == (
            ReturnRequest.RefundStatus.COMPLETED
        ):

            if return_request.refund_status != (
                ReturnRequest.RefundStatus.PROCESSING
            ):
                return Response(
                    {
                        "detail": (
                            "Refund must be processing "
                            "before completion."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not transaction_id.strip():
                return Response(
                    {
                        "detail": (
                            "UPI transaction ID is required "
                            "when completing refund."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return_request.refund_processed_at = (
                timezone.now()
            )

            return_request.refund_transaction_id = (
                transaction_id.strip()
            )

        # -----------------------------------------
        # FAILED
        # -----------------------------------------

        elif new_status == (
            ReturnRequest.RefundStatus.FAILED
        ):

            if not refund_note.strip():
                return Response(
                    {
                        "detail": (
                            "Refund failure reason is required."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # -----------------------------------------
        # REJECTED
        # -----------------------------------------

        elif new_status == (
            ReturnRequest.RefundStatus.REJECTED
        ):

            if not refund_note.strip():
                return Response(
                    {
                        "detail": (
                            "Refund rejection reason is required."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return_request.refund_status = new_status

        if refund_note:
            return_request.refund_note = refund_note

        return_request.save()

        return Response(
            ReturnRequestSerializer(
                return_request,
                context={"request": request},
            ).data
        )


# =========================================================
# RISK ENGINE
# =========================================================

def calculate_return_risk(return_request):

    score = 0
    reasons = []

    proofs = list(
        return_request.proofs.all()
    )

    proof_types = {
        proof.proof_type
        for proof in proofs
    }

    # -------------------------------------------------
    # RULE 1: No product photo
    # -------------------------------------------------

    if (
        ReturnProof.ProofType.CUSTOMER_PRODUCT
        not in proof_types
    ):
        score += 25

        reasons.append(
            "Customer product photo is missing."
        )

    # -------------------------------------------------
    # RULE 2: No label photo
    # -------------------------------------------------

    if (
        ReturnProof.ProofType.CUSTOMER_LABEL
        not in proof_types
    ):
        score += 15

        reasons.append(
            "Customer label photo is missing."
        )

    # -------------------------------------------------
    # RULE 3: Expiry/Batch proof missing
    # -------------------------------------------------

    if (
        ReturnProof.ProofType.CUSTOMER_EXPIRY
        not in proof_types
    ):
        score += 15

        reasons.append(
            "Customer expiry/batch proof is missing."
        )

    # -------------------------------------------------
    # RULE 4: Wrong/expired product reason
    # -------------------------------------------------

    if return_request.reason in [
        ReturnRequest.Reason.WRONG_PRODUCT,
        ReturnRequest.Reason.EXPIRED,
    ]:

        score += 10

        reasons.append(
            "Return reason requires additional "
            "product verification."
        )

    # -------------------------------------------------
    # RULE 5: Missing batch number
    # -------------------------------------------------

    if not return_request.return_batch_number.strip():

        score += 10

        reasons.append(
            "Return batch number was not provided."
        )

    # -------------------------------------------------
    # RULE 6: Missing expiry date
    # -------------------------------------------------

    if not return_request.return_expiry_date:

        score += 10

        reasons.append(
            "Return expiry date was not provided."
        )

    # -------------------------------------------------
    # LIMIT SCORE
    # -------------------------------------------------

    score = min(score, 100)

    # -------------------------------------------------
    # RISK LEVEL
    # -------------------------------------------------

    if score >= 60:

        risk_level = (
            ReturnRequest.RiskLevel.HIGH
        )

    elif score >= 30:

        risk_level = (
            ReturnRequest.RiskLevel.MEDIUM
        )

    else:

        risk_level = (
            ReturnRequest.RiskLevel.LOW
        )

    # -------------------------------------------------
    # SUSPICIOUS FLAG
    # -------------------------------------------------

    suspicious = score >= 60

    return_request.risk_score = score

    return_request.risk_level = risk_level

    return_request.suspicious_reasons = reasons

    return_request.suspicious = suspicious

    if suspicious:

        return_request.status = (
            ReturnRequest.Status.SUSPICIOUS
        )

        # Refund is blocked.
        return_request.refund_status = (
            ReturnRequest.RefundStatus.PENDING
        )

    return_request.save()

    return return_request