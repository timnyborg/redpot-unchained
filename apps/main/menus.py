from django.urls import reverse
from menu import Menu, MenuItem

Menu.add_item("main", MenuItem(
    "Apps",
    reverse("programme:search")
    ))

Menu.add_item("main", MenuItem(
    "Students",
    reverse("programme:search")
    ))

Menu.add_item("main", MenuItem(
    "Modules",
    reverse("module:search")
    ))

programme_children = (
    MenuItem("Search",
             reverse("programme:search"),
             icon="search"),
    MenuItem("New",
             reverse("programme:new"),
             icon="plus",
             separator=True,
             check=lambda request: request.user.has_perm('programme.new')
             )
)

Menu.add_item("main", MenuItem(
    "Programmes",
    '#',
    children=programme_children
    ))

Menu.add_item("main", MenuItem(
    "Tutors",
    reverse("programme:search")
    ))

finance_children = (
    MenuItem("Invoices",
             reverse("invoice:search"),
             icon="search"),
)

Menu.add_item("main", MenuItem(
    "Finance",
    '#',
    children=finance_children
    ))

Menu.add_item("main", MenuItem(
    "Marketing",
    '#',
    ))

Menu.add_item("main", MenuItem(
    "Dev",
    reverse("programme:search"),
    check=lambda request: request.user.is_superuser
    ))

# Right-hand login/user menu
Menu.add_item("user", MenuItem(
    "Login",
    reverse("login"),
    check=lambda request: not request.user.is_authenticated
    ))

# Define children for the my account menu
myaccount_children = (
    MenuItem("Edit Profile",
             None,
             icon="user"),
    MenuItem("Admin",
             reverse("admin:index"),
             separator=True,
             icon='tools',
             check=lambda request: request.user.is_superuser),
    MenuItem(
            "Logout",
            reverse("logout"),
            separator=True,
            icon='sign-out-alt',
            check=lambda request: request.user.is_authenticated
            ),
)

Menu.add_item("user", MenuItem(
    lambda request: request.user.get_full_name,    
    '#',
    icon='user-circle',
    check=lambda request: request.user.is_authenticated,
    children=myaccount_children
    ))
