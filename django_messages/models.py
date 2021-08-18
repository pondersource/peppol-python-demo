from django.conf import settings
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse
from django.db import models
from django.db.models import signals
from django.utils import timezone
from six import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _
from connection.models import Contact

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class MessageManager(models.Manager):

    def suppliers_for(self, user):
        """
        Returns all messages from suppliers.
        """
        suppliers = suppliers = Contact.objects.suppliers(request.user)
        return self.filter(
            sender__in=suppliers,
            recipient_deleted_at__isnull=True,
            sender_deleted_at__isnull=True,
        )
    def costumers_for(self, user):
        """
        Returns all messages from costumers.
        """
        costumers = suppliers = Contact.objects.costumers(request.user)
        return self.filter(
            __in=costumers,
            recipient_deleted_at__isnull=True,
            sender_deleted_at__isnull=True,
        )
    def inbox_for(self, user):
        """
        Returns all messages that were received by the given user and are not
        marked as deleted.
        """
        return self.filter(
            recipient=user,
            recipient_deleted_at__isnull=True,
        )
    def outbox_for(self, user):
        """
        Returns all messages that were sent by the given user and are not
        marked as deleted.
        """
        return self.filter(
            sender=user,
            sender_deleted_at__isnull=True,
        )

    def messages_for(self, user):
        """
        Returns all messages are not marked as deleted.
        """
        return self.filter(
            sender_deleted_at__isnull=True,
            recipient_deleted_at__isnull=True,
        )

    def trash_for(self, user):
        """
        Returns all messages that were either received or sent by the given
        user and are marked as deleted.
        """
        return self.filter(
            recipient=user,
            recipient_deleted_at__isnull=False,
        ) | self.filter(
            sender=user,
            sender_deleted_at__isnull=False,
        )


@python_2_unicode_compatible
class Message(models.Model):
    """
    A private message from user to user
    """
    subject = models.CharField(_("Subject"), max_length=140)
    body = models.TextField(_("Body"))
    sender = models.ForeignKey(AUTH_USER_MODEL, related_name='sent_messages', verbose_name=_("Sender"), on_delete=models.PROTECT)
    recipient = models.ForeignKey(AUTH_USER_MODEL, related_name='received_messages', null=True, blank=True, verbose_name=_("Recipient"), on_delete=models.SET_NULL)
    parent_msg = models.ForeignKey('self', related_name='next_messages', null=True, blank=True, verbose_name=_("Parent message"), on_delete=models.SET_NULL)
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)
    replied_at = models.DateTimeField(_("replied at"), null=True, blank=True)
    sender_deleted_at = models.DateTimeField(_("Sender deleted at"), null=True, blank=True)
    recipient_deleted_at = models.DateTimeField(_("Recipient deleted at"), null=True, blank=True)
    invoice = models.FileField(upload_to=None, max_length=254)
    xml_type = models.CharField(max_length=20, null=True)

    objects = MessageManager()

    def new(self):
        """returns whether the recipient has read the message or not"""
        if self.read_at is None:
            return True
        return False

    def replied(self):
        """returns whether the recipient has written a reply to this message"""
        if self.replied_at is None:
            return False
        return True

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('django_messages:messages_detail', args=[self.id])

    def save(self, **kwargs):
        if not self.id:
            self.sent_at = timezone.now()
        super(Message, self).save(**kwargs)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")


def inbox_count_for(user):
    """
    returns the number of unread messages for the given user but does not
    mark them seen
    """
    unread_messages = Message.objects.filter(recipient=user, read_at__isnull=True, recipient_deleted_at__isnull=True).count()
    if unread_messages == 0:
        return None
    return unread_messages

# fallback for email notification if django-notification could not be found
if "pinax.notifications" not in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from django_messages.utils import new_message_email
    signals.post_save.connect(new_message_email, sender=Message)
