from apps.core.models import User
from apps.core.utils.dates import academic_year
from apps.module.models import Module
from apps.qualification_aim.models import QualificationAim
from apps.student.services import next_husid

from . import models


def create_enrolment(
    *, qa: QualificationAim, module: Module, status: models.EnrolmentStatus, user: User
) -> models.Enrolment:
    """Create an enrolment, while ensuring the student has a husid, qa.start_date is set, etc.
    This is a partial replacement of rp_api's create_enrolment, which has a lot of website-specific functionality
    (fees, overbooking emails, status setting, etc.)
    That functionality should be implemented in an RCP-accessible endpoint which in turn calls this function
    """

    # Create/Lookup HUSID number for student
    if not qa.student.husid:  # None (enquirer)
        qa.student.husid = next_husid(academic_year=academic_year(module.start_date))
        qa.student.save()

    # If the QA doesn't have a start_date (COMDATE), or it's later than the module's, change it
    # todo: determine if qa.start_date has any value now that new hesa instances are generated annually
    if not qa.start_date or module.start_date and qa.start_date > module.start_date:
        qa.start_date = module.start_date
        qa.save()

    enrolment = models.Enrolment.objects.create(
        qa=qa,
        module=module,
        status=status,
        created_by=user.username,
        modified_by=user.username,
    )
    return enrolment
