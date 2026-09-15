
from .models import Notification


def create_notification(
    recipient,
    notification_type,
    title,
    message,
    priority=Notification.Priority.NORMAL,
    reference_id=None,
    reference_type="",
):
    """
    Common function to create a notification.
    """

    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        reference_id=reference_id,
        reference_type=reference_type,
    )


# ============================================================
# ORDER NOTIFICATIONS
# ============================================================

def notify_order_placed(order):
    """
    Customer notification when a new order is placed.
    """

    return create_notification(
        recipient=order.user,
        notification_type=Notification.NotificationType.ORDER_PLACED,
        title="Order Placed",
        message=(
            f"Your order {order.order_number} has been placed successfully."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=order.id,
        reference_type="ORDER",
    )


def notify_order_confirmed(order):
    """
    Customer notification when seller confirms the order.
    """

    return create_notification(
        recipient=order.user,
        notification_type=Notification.NotificationType.ORDER_CONFIRMED,
        title="Order Confirmed",
        message=(
            f"Your order {order.order_number} has been confirmed."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=order.id,
        reference_type="ORDER",
    )


def notify_order_processing(order):
    """
    Customer notification when order processing starts.
    """

    return create_notification(
        recipient=order.user,
        notification_type=Notification.NotificationType.ORDER_PROCESSING,
        title="Order Processing",
        message=(
            f"Your order {order.order_number} is now being processed."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=order.id,
        reference_type="ORDER",
    )


def notify_order_shipped(order):
    """
    Customer notification when order is shipped.
    """

    return create_notification(
        recipient=order.user,
        notification_type=Notification.NotificationType.ORDER_SHIPPED,
        title="Order Shipped",
        message=(
            f"Your order {order.order_number} has been shipped."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=order.id,
        reference_type="ORDER",
    )


def notify_order_out_for_delivery(order):
    """
    Customer notification when order is out for delivery.
    """

    return create_notification(
        recipient=order.user,
        notification_type=Notification.NotificationType.OUT_FOR_DELIVERY,
        title="Out for Delivery",
        message=(
            f"Your order {order.order_number} is out for delivery."
        ),
        priority=Notification.Priority.HIGH,
        reference_id=order.id,
        reference_type="ORDER",
    )


def notify_order_delivered(order):
    """
    Customer notification when order is delivered.
    """

    return create_notification(
        recipient=order.user,
        notification_type=Notification.NotificationType.ORDER_DELIVERED,
        title="Order Delivered",
        message=(
            f"Your order {order.order_number} has been delivered successfully."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=order.id,
        reference_type="ORDER",
    )


def notify_order_cancelled(order):
    """
    Customer notification when order is cancelled.
    """

    return create_notification(
        recipient=order.user,
        notification_type=Notification.NotificationType.ORDER_CANCELLED,
        title="Order Cancelled",
        message=(
            f"Your order {order.order_number} has been cancelled."
        ),
        priority=Notification.Priority.HIGH,
        reference_id=order.id,
        reference_type="ORDER",
    )


def notify_new_order_to_seller(order_item):
    """
    Seller notification when a new order item is created.
    """

    seller_user = order_item.seller

    return create_notification(
        recipient=seller_user,
        notification_type=Notification.NotificationType.NEW_ORDER_SELLER,
        title="New Order Received",
        message=(
            f"You received a new order {order_item.order.order_number} "
            f"for {order_item.product_name}. "
            f"Quantity: {order_item.quantity}."
        ),
        priority=Notification.Priority.HIGH,
        reference_id=order_item.order.id,
        reference_type="ORDER",
    )


# ============================================================
# RETURN NOTIFICATIONS
# ============================================================

def notify_return_requested(return_request):
    """
    Customer notification when return request is created.
    """

    return create_notification(
        recipient=return_request.customer,
        notification_type=Notification.NotificationType.RETURN_REQUESTED,
        title="Return Request Submitted",
        message=(
            f"Your return request for "
            f"{return_request.order_item.product_name} "
            f"has been submitted successfully."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=return_request.id,
        reference_type="RETURN",
    )


def notify_return_approved(return_request):
    """
    Customer notification when return is approved.
    """

    return create_notification(
        recipient=return_request.customer,
        notification_type=Notification.NotificationType.RETURN_APPROVED,
        title="Return Approved",
        message=(
            f"Your return request for "
            f"{return_request.order_item.product_name} "
            "has been approved."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=return_request.id,
        reference_type="RETURN",
    )


def notify_return_rejected(return_request):
    """
    Customer notification when return is rejected.
    """

    return create_notification(
        recipient=return_request.customer,
        notification_type=Notification.NotificationType.RETURN_REJECTED,
        title="Return Rejected",
        message=(
            f"Your return request for "
            f"{return_request.order_item.product_name} "
            "has been rejected."
        ),
        priority=Notification.Priority.HIGH,
        reference_id=return_request.id,
        reference_type="RETURN",
    )


def notify_return_picked_up(return_request):
    """
    Customer notification when return pickup is completed.
    """

    return create_notification(
        recipient=return_request.customer,
        notification_type=Notification.NotificationType.RETURN_PICKED_UP,
        title="Return Picked Up",
        message=(
            f"Your returned "
            f"{return_request.order_item.product_name} "
            "has been picked up."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=return_request.id,
        reference_type="RETURN",
    )


def notify_return_received(return_request):
    """
    Customer notification when returned product is received.
    """

    return create_notification(
        recipient=return_request.customer,
        notification_type=Notification.NotificationType.RETURN_RECEIVED,
        title="Return Received",
        message=(
            f"Your returned "
            f"{return_request.order_item.product_name} "
            "has been received."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=return_request.id,
        reference_type="RETURN",
    )


def notify_suspicious_return(return_request):
    """
    Customer notification when a return is flagged for additional review.

    This does NOT mean the customer is accused of fraud.
    It only means the return needs additional verification.
    """

    return create_notification(
        recipient=return_request.customer,
        notification_type=Notification.NotificationType.SUSPICIOUS_RETURN,
        title="Return Under Additional Review",
        message=(
            f"Your return request for "
            f"{return_request.order_item.product_name} "
            "requires additional verification before it can be completed."
        ),
        priority=Notification.Priority.HIGH,
        reference_id=return_request.id,
        reference_type="RETURN",
    )


# ============================================================
# REFUND NOTIFICATIONS
# ============================================================

def notify_refund_approved(return_request):
    """
    Customer notification when refund is approved.
    """

    return create_notification(
        recipient=return_request.customer,
        notification_type=Notification.NotificationType.REFUND_APPROVED,
        title="Refund Approved",
        message=(
            f"Your refund of ₹{return_request.refund_amount} "
            f"for order {return_request.order.order_number} "
            "has been approved."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=return_request.id,
        reference_type="RETURN",
    )


def notify_refund_processing(return_request):
    """
    Customer notification when refund is being processed.
    """

    return create_notification(
        recipient=return_request.customer,
        notification_type=Notification.NotificationType.REFUND_PROCESSING,
        title="Refund Processing",
        message=(
            f"Your refund of ₹{return_request.refund_amount} "
            "is currently being processed."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=return_request.id,
        reference_type="RETURN",
    )


def notify_refund_completed(return_request):
    """
    Customer notification when refund is successfully completed.
    """

    transaction_text = ""

    if return_request.refund_transaction_id:
        transaction_text = (
            f" Transaction ID: {return_request.refund_transaction_id}."
        )

    return create_notification(
        recipient=return_request.customer,
        notification_type=Notification.NotificationType.REFUND_COMPLETED,
        title="Refund Completed",
        message=(
            f"Your refund of ₹{return_request.refund_amount} "
            f"has been completed via UPI.{transaction_text}"
        ),
        priority=Notification.Priority.HIGH,
        reference_id=return_request.id,
        reference_type="RETURN",
    )


def notify_refund_failed(return_request):
    """
    Customer notification when refund fails.
    """

    return create_notification(
        recipient=return_request.customer,
        notification_type=Notification.NotificationType.REFUND_FAILED,
        title="Refund Failed",
        message=(
            f"Your refund for "
            f"{return_request.order_item.product_name} "
            "could not be completed. Please check your UPI details "
            "or contact support."
        ),
        priority=Notification.Priority.URGENT,
        reference_id=return_request.id,
        reference_type="RETURN",
    )


# ============================================================
# SELLER VERIFICATION NOTIFICATIONS
# ============================================================

def notify_seller_registered(seller_profile):
    """
    Notification for seller after registration.
    """

    return create_notification(
        recipient=seller_profile.user,
        notification_type=Notification.NotificationType.SELLER_REGISTERED,
        title="Seller Registration Submitted",
        message=(
            f"Your seller registration for "
            f"{seller_profile.shop_name} has been submitted "
            "and is awaiting verification."
        ),
        priority=Notification.Priority.NORMAL,
        reference_id=seller_profile.id,
        reference_type="SELLER",
    )


def notify_seller_approved(seller_profile):
    """
    Notification when seller profile is approved.
    """

    return create_notification(
        recipient=seller_profile.user,
        notification_type=Notification.NotificationType.SELLER_APPROVED,
        title="Seller Account Approved",
        message=(
            f"Your seller account for "
            f"{seller_profile.shop_name} has been approved. "
            "You can now use seller marketplace features."
        ),
        priority=Notification.Priority.HIGH,
        reference_id=seller_profile.id,
        reference_type="SELLER",
    )


def notify_seller_rejected(seller_profile):
    """
    Notification when seller profile is rejected.
    """

    return create_notification(
        recipient=seller_profile.user,
        notification_type=Notification.NotificationType.SELLER_REJECTED,
        title="Seller Account Rejected",
        message=(
            f"Your seller account for "
            f"{seller_profile.shop_name} has been rejected."
        ),
        priority=Notification.Priority.HIGH,
        reference_id=seller_profile.id,
        reference_type="SELLER",
    )


# ============================================================
# SYSTEM NOTIFICATION
# ============================================================

def notify_system(
    recipient,
    title,
    message,
    priority=Notification.Priority.NORMAL,
    reference_id=None,
    reference_type="",
):
    """
    Generic system notification helper.
    """

    return create_notification(
        recipient=recipient,
        notification_type=Notification.NotificationType.SYSTEM,
        title=title,
        message=message,
        priority=priority,
        reference_id=reference_id,
        reference_type=reference_type,
    )

