from menu import Menu, MenuItem

from django.urls import reverse

Menu.add_item("staff_forms", MenuItem("Home", reverse("staff_forms:home")))
Menu.add_item("staff_forms", MenuItem("Starter", reverse("staff_forms:starter")))
Menu.add_item("staff_forms", MenuItem("Leaver", reverse("staff_forms:leaver")))
