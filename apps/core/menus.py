from menu import Menu, MenuItem

from django.urls import reverse

Menu.add_item("main", MenuItem("Apps", reverse("programme:search")))

Menu.add_item("main", MenuItem("Students", reverse("student:search")))

module_children = (
    MenuItem("Search", reverse("module:search"), icon="search"),
    MenuItem(
        "New",
        reverse("module:new"),
        icon="plus",
        separator=True,
        check=lambda request: request.user.has_perm('module.new'),
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

tutor_children = (MenuItem("Payment search", reverse("tutor-payment:search"), icon="search"),)

Menu.add_item("main", MenuItem("Tutors", '#', children=tutor_children))

finance_children = [
    MenuItem("Invoices", reverse("invoice:search"), icon="search"),
    MenuItem("Approve change requests", reverse("amendment:approve"), icon="pound-sign"),
    MenuItem(
        "Search change requests",
        reverse("amendment:search"),
        icon="pound-sign",
        check=lambda request: request.user.has_perm('amendment.edit_finance'),
    ),
]

Menu.add_item("main", MenuItem("Finance", '#', children=finance_children))

Menu.add_item(
    "main",
    MenuItem(
        "Marketing",
        '#',
    ),
)


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
            "https://sentry.io/organizations/university-of-oxford-conted/projects/redpot-unchained/",
            icon="bug",
            target="_blank",
        ),
    ]


Menu.add_item("main", MenuItem("Dev", '#', children=dev_children, check=lambda request: request.user.is_superuser))

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
