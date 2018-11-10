from django.test import TestCase
from django.utils import timezone

from core.models import RiskType, Field, Risk, FieldValue, OptionValue


class RiskTypeModelTestCase(TestCase):

    def test_string_representation(self):
        risk_type = RiskType.objects.create(name="Sample Risk Type",
                                            description="Some sample text")
        self.assertEqual(risk_type.__str__(), risk_type.name)


class RiskModelTestCase(TestCase):

    def test_string_representation(self):
        risk_type = RiskType.objects.create(name="Sample Risk Type",
                                            description="Some sample text")
        risk = Risk.objects.create(risk_type=risk_type)
        self.assertEqual(risk.__str__(), risk_type.name)


class OptionValueTestCase(TestCase):

    def test_string_representation(self):
        option = OptionValue.objects.create(value="Sample")
        self.assertEqual(option.__str__(), option.value)


class FieldModelTestCase(TestCase):

    def test_string_representation(self):
        risk_type = RiskType(name="Car", description="Risk template for car")
        risk_type.save()

        field = Field(name="Name", description="Name of car",
                      field_type=Field.TEXT_FIELD, risk_type=risk_type)
        field.save()

        self.assertEqual(field.__str__(), field.name)


class FieldValueModelTestCase(TestCase):

    def test_string_representation(self):
        risk_type = RiskType(name="Car", description="Risk template for car")
        risk_type.save()

        risk = Risk.objects.create(risk_type=risk_type)

        field = Field(name="Name", description="Name of car",
                      field_type=Field.TEXT_FIELD, risk_type=risk_type)
        field.save()

        field_value = FieldValue(field=field, risk=risk, value_text="Honda")
        field_value.save()

        self.assertEqual(field_value.__str__(), field_value.value_text)

    def test_value_property_getter_and_setter_works_with_text_field(self):
        risk_type = RiskType(name="Car", description="Risk template for car")
        risk_type.save()

        text_field = Field(name="Name", description="Name of car",
                           field_type=Field.TEXT_FIELD, risk_type=risk_type)
        text_field.save()

        risk = Risk.objects.create(risk_type=risk_type)

        field_value = FieldValue(field=text_field, risk=risk)
        field_value.value = "Honda"

        self.assertEqual(field_value.value_text, "Honda")

        field_value.save()

        self.assertEqual(field_value.value, field_value.value_text)

    def test_value_property_getter_and_setter_works_with_number_field(self):
        risk_type = RiskType(name="Car", description="Risk template for car")
        risk_type.save()

        number_field = Field(name="Model No.", description="Model serial no.",
                             field_type=Field.NUMBER_FIELD,
                             risk_type=risk_type)
        number_field.save()

        risk = Risk.objects.create(risk_type=risk_type)

        field_value = FieldValue(field=number_field, risk=risk)
        field_value.value = 12345

        self.assertEqual(field_value.value_number, 12345)

        field_value.save()

        self.assertEqual(field_value.value, field_value.value_number)

    def test_value_property_getter_and_setter_works_with_date_field(self):
        risk_type = RiskType(name="Car", description="Risk template for car")
        risk_type.save()

        date_field = Field(name="Purchase Date", field_type=Field.DATE_FIELD,
                           risk_type=risk_type)
        date_field.save()

        risk = Risk.objects.create(risk_type=risk_type)
        field_value = FieldValue(field=date_field, risk=risk)
        field_value.value = timezone.now().date()

        self.assertEqual(field_value.value_date, timezone.now().date())

        field_value.save()

        self.assertEqual(field_value.value, field_value.value_date)

    def test_value_property_getter_and_setter_works_with_enum_field(self):
        risk_type = RiskType(name="Car", description="Risk template for car")
        risk_type.save()

        enum_field = Field(name="Car Type", field_type=Field.ENUM_FIELD,
                           risk_type=risk_type)
        enum_field.save()

        option_sedan = OptionValue.objects.create(value="Sedan")
        option_suv = OptionValue.objects.create(value="SUV")
        option_hatchback = OptionValue.objects.create(value="Hatchback")

        enum_field.options.add(option_suv)
        enum_field.options.add(option_sedan)
        enum_field.options.add(option_hatchback)

        risk = Risk.objects.create(risk_type=risk_type)
        field_value = FieldValue(field=enum_field, risk=risk)
        field_value.value = option_sedan

        self.assertEqual(field_value.value_option, option_sedan)

        field_value.save()

        self.assertEqual(field_value.value, field_value.value_option)
