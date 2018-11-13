from django.db import transaction
from rest_framework import serializers

from core.models import Field, RiskType, OptionValue, Risk, FieldValue


class OptionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionValue
        fields = ('id', 'value')
        extra_kwargs = {
            'value': {
                'help_text': 'Option value'
            }
        }


class FieldSerializer(serializers.ModelSerializer):
    options = OptionValueSerializer(many=True, required=False)

    class Meta:
        model = Field
        fields = ('id', 'name', 'description', 'field_type', 'options')
        extra_kwargs = {
            'field_type': {
                'help_text': 'Data type of value this field supports.'
            },
            'options': {
                'help_text': 'List of available options for this field.'
                             ' Only Required when field_type is enum.'
            },
        }

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
    fields = FieldSerializer(
        many=True, required=True, allow_empty=False,
        help_text='List of fields belonging to this Risk Type')

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


class GenericValueField(serializers.Field):
    """
    Generic representation of "value" of a FieldValue object.

    Using this field all value types can be represented using a single field.

    This can be used for both read and writes.
    """
    def to_representation(self, value):
        # If the value is an option, return it's primary key
        if isinstance(value.value, OptionValue):
            return value.value.id
        # otherwise return the value in it's default type
        return value.value

    def to_internal_value(self, data):
        # assign the data to "value" field
        return {"value": data}


class FieldValueSerializer(serializers.ModelSerializer):
    field = FieldSerializer(
        read_only=True, help_text='Read only list of fields for reference.')
    field_id = serializers.PrimaryKeyRelatedField(
        help_text='Primary Key ID of field the value belongs to.',
        source='field', queryset=Field.objects.all(), required=True)
    value = GenericValueField(
        source="*", help_text='Actual value for the field.'
        ' Returns primary key of option if the field_type is enum.'
        ' The data-type of the value varies based on field_type.')

    class Meta:
        model = FieldValue
        fields = ('id', 'field', 'field_id', 'value')

    def validate(self, data):
        field = data["field"]
        value = data.pop("value")

        # Re-validate the value data
        # This is done because the "value" field is of variant data type,
        # it can accept any type of value.
        #
        # The following code checks whether the supplied value is correct or
        # not by passing it through serializers/validators corresponding
        # their field types.
        try:
            if field.field_type == Field.TEXT_FIELD:
                value_serializer = serializers.CharField()
                data["value_text"] = value_serializer.run_validation(value)

            elif field.field_type == Field.NUMBER_FIELD:
                value_serializer = serializers.IntegerField()
                data["value_number"] = value_serializer.run_validation(value)

            elif field.field_type == Field.DATE_FIELD:
                value_serializer = serializers.DateField()
                data["value_date"] = value_serializer.run_validation(value)

            else:
                # Make sure value is a valid integer (i.e. primary key)
                value_serializer = serializers.IntegerField()
                option_pk = value_serializer.run_validation(value)
                selected_option = field.options.filter(pk=option_pk).first()

                if selected_option is None:
                    raise serializers.ValidationError(
                        "Invalid value. Option value does not exist.")
                else:
                    data["value_option"] = selected_option

        except serializers.ValidationError as e:
            # By default any validation error raised inside .validate
            # is displayed under non_error_fields
            #
            # Re-raise the error with value field as source
            raise serializers.ValidationError({"value": e.detail})

        return data


class RiskSerializer(serializers.ModelSerializer):
    values = FieldValueSerializer(
        source='field_values', many=True, allow_empty=False,
        help_text='List of field_id:value pairs for this risk.'
        ' All of them are required when creating a new risk object.')

    class Meta:
        model = Risk
        fields = ('id', 'risk_type', 'values')
        extra_kwargs = {
            'risk_type': {
                'help_text': 'Primary key ID of risk_type for this risk.'
            }
        }

    def validate(self, data):
        values = data["field_values"]
        field_ids = [value["field"].id for value in values]

        # Make sure all fields for this risk type are submitted
        missed_fields = data["risk_type"].fields.exclude(id__in=field_ids)
        if missed_fields.exists():
            field_names = missed_fields.values_list('name', flat=True)
            field_names = ", ".join(["'%s'" % field for field in field_names])
            raise serializers.ValidationError(
                "All fields are required. %s fields not found." % field_names)

        # If all fields are present, check for duplicates
        if len(field_ids) != len(set(field_ids)):
            raise serializers.ValidationError(
                "Duplicate fields are not allowed.")

        return data

    @transaction.atomic
    def create(self, validated_data):
        values = validated_data.pop('field_values')
        risk = Risk.objects.create(**validated_data)
        # Create field values for risk
        for value in values:
            FieldValue.objects.create(risk=risk, **value)
        return risk
