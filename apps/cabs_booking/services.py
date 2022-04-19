from datetime import date, datetime, timedelta
from typing import Generator

from apps.module.models import Equipment, Module

from . import client, models


def create_module_bookings(*, module: Module, api_client: client.CABSApiClient) -> models.CABSBooking:
    """Attempt booking weekly classes module into its allocated room on CABS.
    api_client is injected as a dependency to allow its reuse (without doing authentication anew each time)
    """
    tutor = module.tutors.filter(tutor_module__is_teaching=True).first()
    tutor_name = tutor.student.formal_name if tutor else ''

    # Make sure the default equipment is set
    module.equipment.add(*Equipment.objects.filter(always_required=True))

    # Create a master booking record
    mbr_id = api_client.create_mbr(
        title=module.title,
        address_1='Weekly Classes office',
        address_2='Ewert House, Ewert Place',
        address_3='Oxford',
        postcode='OX2 7DD',
        phone='+44 (0)1865 280900',
        email='weeklyclasses@conted.ox.ac.uk',
    )

    # Generate session
    session_id = api_client.create_session()
    confirmed = 0
    provisional = 0

    for meeting_date in module_booking_dates(module):
        # Check selected room availability
        available = api_client.check_room_availability(
            starting_at=(datetime.combine(meeting_date, module.start_time)),
            ending_at=(datetime.combine(meeting_date, module.end_time)),
            room_code=module.room.id,
            setup_minutes=15,
        )
        if available:
            confirmed += 1
        else:
            provisional += 1

        # Book the room
        booking_id = api_client.book_room(
            mbr=mbr_id,
            start_date=meeting_date,
            start_time=module.start_time,
            end_time=module.end_time,
            room_code=module.room.id,
            status='CONFRM' if available else 'ANNCOM',
            room_setup=module.room_setup,
            max_size=module.max_size,
            tutor_name=tutor_name,
            session_id=session_id,
        )

        # Add equipment
        equipment = module.moduleequipment_set.select_related('equipment')
        for extra in equipment:
            api_client.add_extra(
                room_sysno=booking_id,
                start_date=meeting_date,
                start_time=module.start_time,
                end_time=module.end_time,
                note=extra.note or extra.equipment.name,
                extra_code=extra.equipment.ewert_cabs_code
                if module.room.building == 'Ewert House'
                else extra.equipment.rewley_cabs_code,
            )
    return module.cabs_bookings.create(mbr_id=mbr_id, confirmed=confirmed, provisional=provisional)


def module_booking_dates(module: Module) -> Generator[date, None, None]:
    """Generator to return all of a weekly class' dates.  Maybe this should sit outside the CABS stuff"""
    next_date = module.start_date
    while next_date <= module.end_date:
        # If a course has midterm dates, then we add weeks until we're out of the midterms
        if not (
            module.hilary_start and module.michaelmas_end and module.michaelmas_end < next_date < module.hilary_start
        ):
            yield next_date
        # Increment a week at a time
        next_date += timedelta(weeks=1)
