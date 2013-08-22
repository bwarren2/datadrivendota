from django.core.exceptions import ValidationError
from settings.base import ADDER_32_BIT


def validate_32bit(value):
    if value <= 0 or value > ADDER_32_BIT:
        raise ValidationError(u'%s is not between 0 and the \
            32 bit conversion number (%s)' % (value,ADDER_32_BIT))
