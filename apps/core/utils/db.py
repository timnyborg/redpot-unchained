from django.db import connection


def next_in_sequence(sequence_name: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT NEXT VALUE FOR {sequence_name}")
        row = cursor.fetchone()
    return row[0]
