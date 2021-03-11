from django.db import connections
from django.db.utils import InterfaceError


class MSSQLMirroringRouter:
    """A router that automatically switches between MSSQL databases in a mirroring session"""

    PRINCIPAL = 'default'
    MIRROR = 'mirror'

    def for_read(self, model, **hints):
        if not self.test_connection_to_db(self.PRINCIPAL):
            self.PRINCIPAL, self.MIRROR = self.MIRROR, self.PRINCIPAL
        return self.PRINCIPAL

    def for_write(self, model, **hints):
        return self.for_read(model, **hints)

    def test_connection_to_db(database_name):
        db_conn = connections[database_name]
        try:
            db_conn.cursor()
        except InterfaceError:
            return False
        else:
            return True
