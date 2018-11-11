from django.db import transaction
from rest_framework import serializers

from core.models import Field, RiskType, OptionValue


class OptionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionValue
        fields = ('id', 'value')


class FieldSerializer(serializers.ModelSerializer):
    options = OptionValueSerializer(many=True, required=False)

    class Meta:
        model = Field
        fields = ('id', 'name', 'description', 'field_type', 'options')

    def validate(self, data):
        options = data.get('options', [])

        # Make sure options are supplied for enum field
        if data["field_type"] == Field.ENUM_FIELD and not options:
            raise serializers.ValidationError(
                {"options": ["This field is required."]}
            )

        # clear options list if this is not an enum field
        if data["field_type"] != Field.ENUM_FIELD:
            options = []

        data["options"] = options

        return data


class RiskTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskType
        fields = ('id', 'name', 'description')


class RiskTypeSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, required=True, allow_empty=False)

    class Meta:
        model = RiskType
        fields = ('id', 'name', 'description', 'fields')

    @transaction.atomic
    def create(self, validated_data):
        fields_data = validated_data.pop('fields', [])
        risk_type = RiskType.objects.create(**validated_data)

        # create fields one-by-one from the supplied field list
        for field_data in fields_data:
            options_data = field_data.pop('options', [])
            field = Field.objects.create(risk_type=risk_type, **field_data)

            # create field options if any
            for option_data in options_data:
                option = OptionValue.objects.create(**option_data)
                field.options.add(option)

        return risk_type

    @transaction.atomic
    def update(self, instance, validated_data):
        # ignore any field changes.
        validated_data.pop('fields', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
