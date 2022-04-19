from menu import Menu, MenuItem

from django.urls import reverse

Menu.add_item("feedback", MenuItem("Results", reverse("feedback:results")))

Menu.add_item("feedback", MenuItem("Questionnaire", reverse("feedback:previewquestions")))

Menu.add_item("feedback", MenuItem("Send requests", reverse("feedback:feedbackrequest")))

Menu.add_item("feedback", MenuItem("Recently finished courses", reverse("feedback:recently-completed")))
