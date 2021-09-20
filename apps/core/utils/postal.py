from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional

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


class FormattedAddress:
    """Takes an address-compatible Model and produces a list based on the country's correct mailing format
    Can produce a newline-separated string for print, or a list of strings for pdfs, html, etc.
    """

    def __init__(self, address: Optional[AddressModel]):
        # If passed None (for example, if a student lacks an address, the address is an empty list)
        if not address:
            self._lines = []
            return

        # Find an entry in the format dictionary that contains the address' country, and get the format
        format_ = next(
            (
                format_
                for (countries, format_) in ADDRESS_FORMATS.items()
                if (address.country or '').lower() in countries
            ),
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
        self._lines = [line for line in raw_lines if line]

    def as_list(self) -> list[str]:
        return self._lines

    def as_string(self) -> str:
        return str(self)

    def __str__(self, separator: str = '\n') -> str:
        return separator.join(self._lines)

    def __iter__(self) -> Iterator[str]:
        return iter(self._lines)
