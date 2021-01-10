from django.conf import settings
import socket

def test_connection_to_db(database_name):
    try:
        db_definition = getattr(settings, 'DATABASES')[database_name]
        s = socket.create_connection((db_definition['HOST'], db_definition.get('PORT', 1433)), 5)
        s.close()
        return True
    except Exception as e:
    #except(AttributeError, socket.timeout) as e:
        return False

class FailoverRouter:
    """A router that defaults reads to the follower but provides a failover back to the default"""
    def db_for_read(self, model, **hints):
        if test_connection_to_db('default'):
            return 'default'
        return 'mirror'

    def db_for_write(self, model, **hints):
        if test_connection_to_db('default'):
            return 'default'
        return 'mirror'