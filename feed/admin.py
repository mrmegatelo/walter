from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

# Register your models here.
from .models import Feed, FeedItem, UserSettings, WaitlistRequest, Invite


class UserSettingsInline(admin.StackedInline):
    model = UserSettings
    can_delete = False
    verbose_name_plural = 'User Settings'


class UserAdmin(BaseUserAdmin):
    inlines = [UserSettingsInline]


class FeedAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'pub_date']
    prepopulated_fields = {'slug': ('title',)}


class FeedItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'feed', 'pub_date']
    list_filter = ['feed']
    search_fields = ['title', 'description']


@admin.action(description='Send selected invites')
def send_invite(modeladmin, request, queryset):
    for invite in queryset:
        user = invite.user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        context = {
            'uid': uid,
            'token': token
        }
        from_email = 'no-reply@thewalter.app'
        to_email = invite.user.email

        subject = loader.render_to_string('emails/registration/invite_subject.txt', context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string('emails/registration/invite_text.html', context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        html_email = loader.render_to_string('emails/registration/invite.html', context)
        email_message.attach_alternative(html_email, "text/html")

        email_message.send()

        invite.status = Invite.Status.SENT
        invite.sent_at = timezone.now()
        invite.save()


class InviteAdmin(admin.ModelAdmin):
    list_display = ['status', 'user', 'created_at', 'sent_at', 'accepted_at', 'activated_at']
    list_editable = ['user']
    list_filter = ['status']
    search_fields = ['email']
    actions = [send_invite]


class WaitlistRequestAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at', 'invite']
    list_filter = ['invite__status']
    list_editable = ['invite']


admin.site.unregister(User)

admin.site.register(User, UserAdmin)
admin.site.register(Feed, FeedAdmin)
admin.site.register(FeedItem, FeedItemAdmin)
admin.site.register(Invite, InviteAdmin)
admin.site.register(WaitlistRequest, WaitlistRequestAdmin)
