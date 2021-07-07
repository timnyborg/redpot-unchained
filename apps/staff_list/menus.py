from menu import Menu, MenuItem

from django.urls import reverse

Menu.add_item("staff_list", MenuItem("Facewall", reverse("staff_list:wall")))

Menu.add_item("staff_list", MenuItem("Contact list", reverse("staff_list:list")))

Menu.add_item("staff_list", MenuItem("Course list", reverse("staff_list:courses")))
