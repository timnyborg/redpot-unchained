from menu import Menu, MenuItem

from django.urls import reverse

Menu.add_item("staff_listing", MenuItem("Facewall", reverse("staff_listing:wall")))

Menu.add_item("staff_listing", MenuItem("Contact list", reverse("staff_listing:list")))

Menu.add_item("staff_listing", MenuItem("Course list", reverse("staff_listing:courses")))
