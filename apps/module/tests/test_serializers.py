from unittest.mock import PropertyMock, patch

from django import test

from .. import models
from ..serializers import ModuleSerializer
from . import factories


class TestModuleSerializer(test.TestCase):
    @patch.object(models.Module, 'update_status')
    def test_autoupdate_calls_update_status(self, mock_method):
        module = factories.ModuleFactory.build()
        serializer = ModuleSerializer(instance=module, data={'auto_publish': True})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(mock_method.called)

    @patch.object(models.Module, 'is_publishable', new_callable=PropertyMock)
    def test_nonpublishable_raises_error(self, mock_is_publishable):
        module = factories.ModuleFactory.build()

        # Should raise an error if not publishable
        serializer = ModuleSerializer(instance=module, data={'is_published': True})
        mock_is_publishable.return_value = False
        self.assertFalse(serializer.is_valid())
        self.assertIn('is_published', serializer.errors)

        # No error otherwise
        serializer = ModuleSerializer(instance=module, data={'is_published': True})
        mock_is_publishable.return_value = True
        self.assertTrue(serializer.is_valid())
