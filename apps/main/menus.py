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

Menu.add_item("main", MenuItem(
    "Programmes",
    reverse("programme:search")
    ))

Menu.add_item("main", MenuItem(
    "Tutors",
    reverse("programme:search")
    ))

Menu.add_item("main", MenuItem(
    "Finance",
    reverse("programme:search")
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

Menu.add_item("user", MenuItem(
    "Logout",
    reverse("logout"),
    check=lambda request: request.user.is_authenticated
    ))

