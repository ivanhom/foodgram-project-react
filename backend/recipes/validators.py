from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class MinMaxValidator:
    """Проверка значения на соответствие указанному диапазону чисел."""
    def __init__(self, min_value, max_value, message):
        self.min_value = min_value
        self.max_value = max_value
        self.message = message

    def __call__(self, value):
        if not (self.min_value <= value <= self.max_value):
            raise ValidationError(self.message)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.min_value == other.min_value
            and self.max_value == other.max_value
            and self.message == other.message
        )
