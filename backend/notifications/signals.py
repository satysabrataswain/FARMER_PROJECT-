from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from orders.models import Order, OrderItem
from delivery.models import Delivery
from returns.models import ReturnRequest

from .models import Notification
from .services import (
    create_notification,
    notify_order_placed,
    notify_order_confirmed,
    notify_order_shipped,
    notify_order_out_for_delivery,
    notify_order_delivered,
    notify_order_cancelled,
    notify_return_requested,
    notify_return_approved,
    notify_return_rejected,
    notify_return_received,
    notify_refund_approved,
    notify_refund_processing,
    notify_refund_completed,
    notify_refund_failed,
    notify_suspicious_return,
)


# =========================================================
# ORDER
# =========================================================

@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance, **kwargs):

    if not instance.pk:
        instance._old_order_status = None
        return

    try:
        old_order = Order.objects.get(
            pk=instance.pk
        )

        instance._old_order_status = (
            old_order.order_status
        )

    except Order.DoesNotExist:
        instance._old_order_status = None


@receiver(post_save, sender=Order)
def order_post_save(
    sender,
    instance,
    created,
    **kwargs,
):

    # New order
    if created:

        notify_order_placed(instance)

        return

    old_status = getattr(
        instance,
        "_old_order_status",
        None,
    )

    new_status = instance.order_status

    if old_status == new_status:
        return

    # CONFIRMED
    if new_status == Order.OrderStatus.CONFIRMED:

        notify_order_confirmed(instance)

    # PROCESSING
    elif new_status == Order.OrderStatus.PROCESSING:

        create_notification(
            recipient=instance.user,
            notification_type=(
                Notification.NotificationType.ORDER_PROCESSING
            ),
            title="Order Processing",
            message=(
                f"Your order {instance.order_number} "
                "is now being processed."
            ),
            reference_id=instance.id,
            reference_type="ORDER",
        )

    # SHIPPED
    elif new_status == Order.OrderStatus.SHIPPED:

        notify_order_shipped(instance)

    # OUT FOR DELIVERY
    elif new_status == Order.OrderStatus.OUT_FOR_DELIVERY:

        notify_order_out_for_delivery(instance)

    # DELIVERED
    elif new_status == Order.OrderStatus.DELIVERED:

        notify_order_delivered(instance)

    # CANCELLED
    elif new_status == Order.OrderStatus.CANCELLED:

        notify_order_cancelled(instance)


# =========================================================
# SELLER NEW ORDER
# =========================================================

@receiver(post_save, sender=OrderItem)
def order_item_post_save(
    sender,
    instance,
    created,
    **kwargs,
):

    if not created:
        return

    seller = instance.seller

    # Avoid duplicate notification if the same
    # order item signal somehow fires again.
    already_exists = Notification.objects.filter(
        recipient=seller,
        notification_type=(
            Notification.NotificationType.NEW_ORDER_SELLER
        ),
        reference_id=instance.order_id,
        reference_type="ORDER",
        message__contains=instance.product_name,
    ).exists()

    if already_exists:
        return

    create_notification(
        recipient=seller,
        notification_type=(
            Notification.NotificationType.NEW_ORDER_SELLER
        ),
        title="New Order Received",
        message=(
            f"You received a new order "
            f"{instance.order.order_number} "
            f"for {instance.product_name}."
        ),
        priority=Notification.Priority.HIGH,
        reference_id=instance.order_id,
        reference_type="ORDER",
    )


# =========================================================
# DELIVERY
# =========================================================

@receiver(pre_save, sender=Delivery)
def delivery_pre_save(
    sender,
    instance,
    **kwargs,
):

    if not instance.pk:
        instance._old_delivery_status = None
        return

    try:
        old_delivery = Delivery.objects.get(
            pk=instance.pk
        )

        instance._old_delivery_status = (
            old_delivery.status
        )

    except Delivery.DoesNotExist:
        instance._old_delivery_status = None


@receiver(post_save, sender=Delivery)
def delivery_post_save(
    sender,
    instance,
    created,
    **kwargs,
):

    if created:
        return

    old_status = getattr(
        instance,
        "_old_delivery_status",
        None,
    )

    new_status = instance.status

    if old_status == new_status:
        return

    order = instance.order

    # PICKED UP
    if new_status == Delivery.Status.PICKED_UP:

        create_notification(
            recipient=order.user,
            notification_type=(
                Notification.NotificationType.SYSTEM
            ),
            title="Order Picked Up",
            message=(
                f"Your order {order.order_number} "
                "has been picked up."
            ),
            priority=Notification.Priority.NORMAL,
            reference_id=order.id,
            reference_type="ORDER",
        )

    # IN TRANSIT
    elif new_status == Delivery.Status.IN_TRANSIT:

        create_notification(
            recipient=order.user,
            notification_type=(
                Notification.NotificationType.SYSTEM
            ),
            title="Order In Transit",
            message=(
                f"Your order {order.order_number} "
                "is in transit."
            ),
            priority=Notification.Priority.NORMAL,
            reference_id=order.id,
            reference_type="ORDER",
        )

    # OUT FOR DELIVERY
    elif new_status == Delivery.Status.OUT_FOR_DELIVERY:

        notify_order_out_for_delivery(order)

    # DELIVERED
    #
    # Order model ka status bhi delivery view mein
    # DELIVERED ho raha hai, isliye duplicate avoid karne ke
    # liye yahan Order Delivered notification create nahi karenge.
    elif new_status == Delivery.Status.DELIVERED:

        return


# =========================================================
# RETURN
# =========================================================

@receiver(pre_save, sender=ReturnRequest)
def return_pre_save(
    sender,
    instance,
    **kwargs,
):

    if not instance.pk:

        instance._old_return_status = None
        instance._old_refund_status = None

        return

    try:
        old_return = ReturnRequest.objects.get(
            pk=instance.pk
        )

        instance._old_return_status = (
            old_return.status
        )

        instance._old_refund_status = (
            old_return.refund_status
        )

    except ReturnRequest.DoesNotExist:

        instance._old_return_status = None
        instance._old_refund_status = None


@receiver(post_save, sender=ReturnRequest)
def return_post_save(
    sender,
    instance,
    created,
    **kwargs,
):

    old_return_status = getattr(
        instance,
        "_old_return_status",
        None,
    )

    old_refund_status = getattr(
        instance,
        "_old_refund_status",
        None,
    )

    # -----------------------------------------------------
    # NEW RETURN
    # -----------------------------------------------------

    if created:

        # If risk engine immediately marked it suspicious,
        # customer gets suspicious notification.
        if instance.status == ReturnRequest.Status.SUSPICIOUS:

            notify_suspicious_return(instance)

        else:

            notify_return_requested(instance)

        return

    # -----------------------------------------------------
    # RETURN STATUS CHANGED
    # -----------------------------------------------------

    new_return_status = instance.status

    if old_return_status != new_return_status:

        # APPROVED
        if new_return_status == (
            ReturnRequest.Status.APPROVED
        ):

            notify_return_approved(instance)

        # REJECTED
        elif new_return_status == (
            ReturnRequest.Status.REJECTED
        ):

            notify_return_rejected(instance)

        # PICKED UP
        elif new_return_status == (
            ReturnRequest.Status.PICKED_UP
        ):

            create_notification(
                recipient=instance.customer,
                notification_type=(
                    Notification.NotificationType.RETURN_PICKED_UP
                ),
                title="Return Picked Up",
                message=(
                    f"Your return for "
                    f"{instance.order_item.product_name} "
                    "has been picked up."
                ),
                priority=Notification.Priority.NORMAL,
                reference_id=instance.id,
                reference_type="RETURN",
            )

        # RECEIVED
        elif new_return_status == (
            ReturnRequest.Status.RECEIVED
        ):

            notify_return_received(instance)

        # SUSPICIOUS
        elif new_return_status == (
            ReturnRequest.Status.SUSPICIOUS
        ):

            notify_suspicious_return(instance)

    # -----------------------------------------------------
    # REFUND STATUS CHANGED
    # -----------------------------------------------------

    new_refund_status = instance.refund_status

    if old_refund_status == new_refund_status:
        return

    # REFUND APPROVED
    if new_refund_status == (
        ReturnRequest.RefundStatus.APPROVED
    ):

        notify_refund_approved(instance)

    # REFUND PROCESSING
    elif new_refund_status == (
        ReturnRequest.RefundStatus.PROCESSING
    ):

        notify_refund_processing(instance)

    # REFUND COMPLETED
    elif new_refund_status == (
        ReturnRequest.RefundStatus.COMPLETED
    ):

        notify_refund_completed(instance)

    # REFUND FAILED
    elif new_refund_status == (
        ReturnRequest.RefundStatus.FAILED
    ):

        notify_refund_failed(instance)