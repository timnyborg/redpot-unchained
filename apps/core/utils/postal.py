from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import AddressModel


ADDRESS_FORMATS = {
    'default': ['{line1}', '{line2}', '{line3}', '{town}', '{countystate}', '{postcode}', '{country}'],
    (
        'england',
        'scotland',
        'northern ireland',
        'wales',
        'united kingdom',
        'uk',
        'united kingdom (england)',
        'united kingdom (scotland)',
        'united kingdom (ireland)',
        'united kingdom (wales)',
    ): [
        '{line1}',
        '{line2}',
        '{line3}',
        '{town}',
        '{countystate}',
        '{postcode}',
    ],
    ('canada', 'australia', 'new zealand'): [
        '{line1}',
        '{line2}',
        '{line3}',
        '{town}',
        '{countystate} {postcode}',
        '{country}',
    ],
    ('usa', 'united states', 'united states of america'): [
        '{line1}',
        '{line2}',
        '{line3}',
        '{town} {countystate} {postcode}',
        '{country}',
    ],
    (
        'algeria',
        'andorra',
        'argentina',
        'armenia',
        'austria',
        'azerbaijan',
        'belarus',
        'belgium',
        'bosnia and herzegovina',
        'bulgaria',
        'croatia',
        'cyprus',
        'czech republic',
        'czechoslovakia',
        'denmark',
        'estonia',
        'ethiopia',
        'faroe islands',
        'finland',
        'france',
        'georgia',
        'germany',
        'greece',
        'greenland',
        'guinea-bissau',
        'haiti',
        'holland',
        'iceland',
        'iran',
        'israel',
        'italy',
        'kuwait',
        'laos',
        'liberia',
        'liechtenstein',
        'lithuania',
        'luxembourg',
        'macedonia',
        'madagascar',
        'mexico',
        'moldova',
        'monaco',
        'montenegro',
        'morocco',
        'netherlands',
        'new caledonia',
        'niger',
        'norway',
        'palestine',
        'paraguay',
        'poland',
        'portugal',
        'romania',
        'san marino',
        'senegal',
        'serbia',
        'slovakia',
        'slovenia',
        'sweden',
        'switzerland',
        'syria',
        'tajikistan',
        'tunisia',
        'turkey',
        'turkmenistan',
        'vatican city',
        'zambia',
    ): [
        '{line1}',
        '{line2}',
        '{line3}',
        '{postcode} {town}',
        '{country}',
    ],
    ('china', 'philippines'): [
        '{line1}',
        '{line2}',
        '{line3}',
        '{town}',
        '{postcode} {countystate}',
        '{country}',
    ],
    ('japan',): [
        '{line1}',
        '{line2}',
        '{line3}',
        '{town} {postcode}',
        '{country}',
    ],
    ('spain',): [
        '{line1}',
        '{line2}',
        '{line3}',
        '{postcode} {town} ({countystate})',
        '{country}',
    ],
    ('ireland',): [
        '{line1}',
        '{line2}',
        '{line3}',
        '{town}',
        '{countystate}',
        '{country}',
    ],
}


def format_address(address: AddressModel) -> list[str]:
    """Takes a dictionary (or Row) and produces a list based on the country's correct mailing format"""
    # todo: turn into a class with methods to return a list or \n-separated string
    # Find an entry in the format dictionary that contains the address' country, and get the format

    format_ = next(
        (format_ for (countries, format_) in ADDRESS_FORMATS.items() if (address.country or '').lower() in countries),
        ADDRESS_FORMATS['default'],
    )

    # Create a set of rows from the format
    raw_lines = [
        line.format(
            line1=address.line1 or '',
            line2=address.line2 or '',
            line3=address.line3 or '',
            town=(address.town or '').upper(),
            countystate=(address.countystate or '').upper(),
            country=(address.country or '').upper(),
            postcode=address.postcode or '',
        )
        for line in format_
    ]
    # Filter out the empty rows
    lines = [line for line in raw_lines if line]
    return lines
