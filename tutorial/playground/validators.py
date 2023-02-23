from rest_framework import serializers


def even_number(value):
    if value % 2 != 0:
        raise serializers.ValidationError('This field must be an even number.')


class MultipleOf:
    def __init__(self, base):
        self.base = base

    def __call__(self, value):
        if value % self.base != 0:
            message = f'This field must be a multiple of {self.base}'
            raise serializers.ValidationError(message)
