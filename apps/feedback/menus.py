from menu import Menu, MenuItem

from django.urls import reverse

Menu.add_item("feedback", MenuItem("Results", reverse("feedback:home")))

Menu.add_item("feedback", MenuItem("Questionnaire", reverse("feedback:home")))

Menu.add_item("feedback", MenuItem("Send requests", reverse("feedback:home")))

Menu.add_item("feedback", MenuItem("Recently finished courses", reverse("feedback:home")))
