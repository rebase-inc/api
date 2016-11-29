import unittest

import marshmallow.exceptions

from ....common.exceptions import (
    marshmallow_exceptions,
    MarshallingError,
    UnmarshallingError,
    ForcedError,
)
from ....common.schema import ValidationError

from . import RebaseModelTestCase


class TestMarshmallowExceptions(RebaseModelTestCase):

    def raise_marshalling(self):
        with marshmallow_exceptions({}):
            raise marshmallow.exceptions.MarshallingError('dummy')

    def test_marshalling_error(self):
        self.assertRaises(MarshallingError, self.raise_marshalling)

    def raise_unmarshalling(self):
        with marshmallow_exceptions({}):
            raise marshmallow.exceptions.UnmarshallingError('dummy')

    def test_unmarshalling_error(self):
        self.assertRaises(UnmarshallingError, self.raise_unmarshalling)

    def raise_validation(self):
        with marshmallow_exceptions({}):
            raise marshmallow.exceptions.ValidationError('dummy')

    def test_validation_error(self):
        self.assertRaises(ValidationError, self.raise_validation)

    def raise_forced(self):
        with marshmallow_exceptions({}):
            raise marshmallow.exceptions.ForcedError('dummy')

    def test_forced_error(self):
        self.assertRaises(ForcedError, self.raise_forced)

