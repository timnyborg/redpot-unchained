from django.db.models import TextChoices


class ELQValues(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/FundingAndMonitoring/field/ELQ"""

    ELQ = '01'
    NOT_ELQ = '03'


class FundingCompletionValues(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/FundingAndMonitoring/field/ELQ"""

    COMPLETED = '01'
    DID_NOT_COMPLETE = '02'
    NOT_YET_COMPLETE = '03'


class EngagementEndReasons(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/Leaver/field/RSNENGEND"""

    AWARDED_CREDIT = "01"
    DEATH = "05"
    NO_CREDIT = "11"
    CREDIT_NOT_YET_KNOWN = "98"


class ModuleResults(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/ModuleInstance/field/MODULERESULT"""

    PASSED = "01"
    FAILED = "06"


class ModuleOutcomes(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/ModuleInstance/field/MODULEOUTCOME"""

    COMPLETE = "01"
    DID_NOT_COMPLETE = "03"
    NOT_FOR_CREDIT = "04"
    NOT_YET_KNOWN = "05"
    NOT_CODED = "96"


class Sexes(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/Student/field/SEXID"""

    FEMALE = "10"
    MALE = "11"
    OTHER = "12"
    PREFER_NOT_TO_SAY = "98"
    NOT_AVAILABLE = "99"


gender_to_sexid_map = {
    'M': Sexes.MALE,
    'F': Sexes.FEMALE,
    'I': Sexes.OTHER,
}


class DistanceValues(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/StudyLocation/field/DISTANCE"""

    IN_UK = "01"
    OUTSIDE_THE_UK = "02"  # likely never to be needed


class HomeFeeEligibility(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/Engagement/field/FEEELIG"""

    ELIGIBLE = "01"
    NOT_ELIGIBLE = "02"
    NOT_ASSESSED = "03"
