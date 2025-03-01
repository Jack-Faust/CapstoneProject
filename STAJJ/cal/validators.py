from django.core.exceptions import ValidationError


def validate_end_before_start(value, start_time):
    """Raise a ValidationError if the value doesn't start with the
    word 'Amazing'.
    """
    if value < start_time:
        msg = 'End time must occur after start time'
        raise ValidationError(msg)