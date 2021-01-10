from django.urls import reverse
from menu import Menu, MenuItem

Menu.add_item("main", MenuItem(
    "Apps",
    reverse("programme:view", args=[270])
    ))

Menu.add_item("main", MenuItem(
    "Students",
    reverse("programme:view", args=[270])
    ))

Menu.add_item("main", MenuItem(
    "Modules",
    reverse("programme:view", args=[270])
    ))

Menu.add_item("main", MenuItem(
    "Programmes",
    reverse("programme:view", args=[270])
    ))

Menu.add_item("main", MenuItem(
    "Tutors",
    reverse("programme:view", args=[270])
    ))

Menu.add_item("main", MenuItem(
    "Finance",
    reverse("programme:view", args=[270])
    ))
    
Menu.add_item("main", MenuItem(
    "Dev",
    reverse("programme:view", args=[270]),
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

