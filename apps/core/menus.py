from menu import Menu, MenuItem

from django.conf import settings
from django.urls import reverse

student_children = (
    MenuItem("Search", reverse("student:search"), icon="search"),
    MenuItem("New", reverse("student:new"), icon="plus", separator=True),
)

Menu.add_item("main", MenuItem("Students", '#', children=student_children))

module_children = (
    MenuItem("Search", reverse("module:search"), icon="search"),
    MenuItem("New", reverse("module:new"), icon="plus", separator=True),
    MenuItem(
        "Proposals",
        'not-implemented',
        icon="graduation-cap",
        separator=True,
        check=lambda request: request.user.has_perm('proposal.create'),
    ),
    MenuItem(
        "Upload to Cabs",
        'not-implemented',
        icon="taxi",
        check=lambda request: request.user.has_perm('module.upload_to_cabs'),
    ),
)

Menu.add_item("main", MenuItem("Modules", '#', children=module_children))

programme_children = (
    MenuItem("Search", reverse("programme:search"), icon="search"),
    MenuItem(
        "New",
        reverse("programme:new"),
        icon="plus",
        separator=True,
        check=lambda request: request.user.has_perm('programme.new'),
    ),
)

Menu.add_item("main", MenuItem("Programmes", '#', children=programme_children))

tutor_children = (
    MenuItem("Search", reverse("student:search") + '?tutors_only=on', icon="search"),
    MenuItem(
        "Payments",
        '#',
        icon="pound-sign",
        children=(
            MenuItem("Search", reverse('tutor-payment:search'), icon="search"),
            MenuItem(
                "Approve",
                reverse("tutor-payment:approve"),
                icon="check",
                check=lambda request: request.user.has_perm('tutor_payment.approve'),
            ),
        ),
    ),
    MenuItem(
        "Contracts",
        '#',
        icon="pencil-alt",
        children=(
            MenuItem("Search", 'not-implemented', icon="search"),
            MenuItem(
                "Approve",
                'not-implemented',
                icon="check",
                check=lambda request: request.user.has_perm('contract.approve'),
            ),
            MenuItem(
                "Sign",
                reverse("amendment:search"),
                icon="signature",
                check=lambda request: request.user.has_perm('contract.sign'),
            ),
        ),
    ),
    MenuItem("New", reverse("student:new"), icon="plus", separator=True),  # todo: consider auto-make-tutor flag
)

Menu.add_item("main", MenuItem("Tutors", '#', children=tutor_children))

finance_children = [
    MenuItem("Invoices", reverse("invoice:search"), icon="file-invoice-dollar"),
    MenuItem(
        "Change requests",
        reverse("invoice:search"),
        icon="pencil-alt",
        children=(
            MenuItem("Approve", reverse("amendment:approve"), icon="check"),
            MenuItem(
                "Search",
                reverse("amendment:search"),
                icon="search",
                check=lambda request: request.user.has_perm('amendment.edit_finance'),
            ),
        ),
    ),
    MenuItem("My batches", 'not-implemented', icon="file-alt", separator=True),
    MenuItem(
        "All batches",
        reverse('finance:all-batches'),
        icon="file-alt",
        check=lambda request: request.user.has_perm('finance'),
    ),
    MenuItem(
        "Upload RCP",
        'not-implemented',
        separator=True,
        icon="upload",
        check=lambda request: request.user.has_perm('finance'),
    ),
    MenuItem(
        "Paypush",
        'not-implemented',
        icon="credit-card",
        check=lambda request: request.user.has_perm('finance'),
    ),
]

Menu.add_item("main", MenuItem("Finance", '#', children=finance_children))


def dev_children(request):
    return [
        MenuItem(
            "View on redpot-staging",
            f'https://redpot-staging.conted.ox.ac.uk{request.get_full_path()}',
            icon="server",
            target='_blank',
        ),
        MenuItem(
            "sentry.io",
            settings.SENTRY_URL,
            icon="bug",
            target="_blank",
        ),
        MenuItem(
            "Gitlab issues",
            "https://gitlab.conted.ox.ac.uk/django/redpot-unchained/issues/",
            icon="gitlab fab",
            target="_blank",
            separator=True,
        ),
        MenuItem(
            "Analytics",
            settings.ANALYTICS_URL,
            icon="chart-area",
            target="_blank",
            separator=True,
        ),
    ]


Menu.add_item("main", MenuItem("Dev", '#', children=dev_children, check=lambda request: request.user.is_superuser))

other_children = (
    MenuItem(
        "Marketing",
        '#',
        icon='money-bill-wave',
        check=lambda request: request.user.has_perm('login'),
        children=(
            MenuItem('Brochures', 'not-implemented', icon='map'),
            MenuItem('Discounts', 'not-implemented', icon='tags'),
            MenuItem('Import opt-ins', 'not-implemented', icon='check'),
        ),
    ),
    MenuItem("Staff listing", reverse('staff_list:home'), icon='users'),
    MenuItem(
        'Transcripts',
        reverse('transcript:create-batch'),
        icon='graduation-cap',
        check=lambda request: request.user.has_perm('transcript.batch_print'),
    ),
)

Menu.add_item("main", MenuItem("Other", '#', children=other_children))


# Right-hand login/user menu
Menu.add_item("user", MenuItem("Login", reverse("login"), check=lambda request: not request.user.is_authenticated))


# Define children for the my account menu
def myaccount_children(request):
    return [
        MenuItem("Edit Profile", reverse("user:profile"), icon="user-edit"),
        MenuItem("View Profile", request.user.get_absolute_url(), icon="user"),
        MenuItem(
            "Admin",
            reverse("admin:index"),
            separator=True,
            icon='tools',
            check=lambda request: request.user.is_superuser,
        ),
        MenuItem(
            "Logout",
            reverse("logout"),
            separator=True,
            icon='sign-out-alt',
            check=lambda request: request.user.is_authenticated,
        ),
    ]


Menu.add_item(
    "user",
    MenuItem(
        lambda request: request.user.get_full_name,
        '#',
        icon='user-circle',
        check=lambda request: request.user.is_authenticated,
        children=myaccount_children,
    ),
)
