import json

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

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


class RiskTypeAPITestCase(APITestCase):
    def test_risk_type_api_post_works_with_valid_data(self):
        data = {
            "name": "Sample Risk Type",
            "fields": [
                {"name": "Field Name", "field_type": "text"}
            ]
        }
        response = self.client.post("/api/risk_types/", data, format="json")
        self.assertEqual(response.status_code, 201)

        risk_type = RiskType.objects.first()
        self.assertIsNotNone(risk_type)
        self.assertEqual(risk_type.name, data["name"])
        self.assertEqual(risk_type.fields.count(), 1)

        field = risk_type.fields.first()
        self.assertEqual(field.name, data["fields"][0]["name"])

    def test_risk_type_api_post_options_required_for_enum_field(self):
        data = {
            "name": "Sample Risk Type",
            "fields": [
                {"name": "Field Name", "field_type": "enum"}
            ]
        }
        response = self.client.post("/api/risk_types/", data, format="json")
        self.assertEqual(response.status_code, 400)

        json_response = response.json()

        self.assertIn("required", json_response["fields"][0]["options"][0])

        risk_type = RiskType.objects.first()
        self.assertIsNone(risk_type)

    def test_risk_type_api_post_options_with_enum_field(self):
        data = {
            "name": "Sample Risk Type",
            "fields": [{
                "name": "Field Name",
                "field_type": "enum",
                "options": [
                    {"value": "Enum Value 1"},
                    {"value": "Enum Value 2"},
                ]
            }]
        }
        response = self.client.post("/api/risk_types/", data, format="json")
        self.assertEqual(response.status_code, 201)

        risk_type = RiskType.objects.first()
        self.assertIsNotNone(risk_type)
        self.assertEqual(risk_type.name, data["name"])
        self.assertEqual(risk_type.fields.count(), 1)

        field = risk_type.fields.first()
        self.assertEqual(field.name, data["fields"][0]["name"])
        self.assertEqual(field.options.count(), 2)

        self.assertEqual(field.options.first().value, "Enum Value 1")
        self.assertEqual(field.options.last().value, "Enum Value 2")


class RiskAPITestCase(APITestCase):
    def test_risk_api_post_works_with_valid_data(self):
        risk_type = RiskType.objects.create(name="Cars")
        text_field = Field.objects.create(name="Name", risk_type=risk_type,
                                          field_type=Field.TEXT_FIELD)

        self.assertEqual(risk_type.risks.count(), 0)

        post_data = {
            "risk_type": risk_type.id,
            "values": [
                {
                    "field_id": text_field.id,
                    "value": "Hyundai"
                }
            ]
        }

        response = self.client.post("/api/risks/", post_data, format="json")
        self.assertEqual(response.status_code, 201)

        self.assertEqual(risk_type.risks.count(), 1)

        created_risk = risk_type.risks.first()
        created_field_value = created_risk.field_values.first()

        self.assertEqual(created_field_value.field.id, text_field.id)
        self.assertEqual(created_field_value.value, "Hyundai")

    def test_risk_api_post_works_with_all_field_types(self):
        risk_type = RiskType.objects.create(name="Cars")

        text_field = Field.objects.create(
            name="Name", risk_type=risk_type, field_type=Field.TEXT_FIELD)

        number_field = Field.objects.create(
            name="Model No.", risk_type=risk_type,
            field_type=Field.NUMBER_FIELD)

        date_field = Field.objects.create(
            name="Purchase date", risk_type=risk_type,
            field_type=Field.DATE_FIELD)

        option_field = Field.objects.create(
            name="Car Type", risk_type=risk_type,
            field_type=Field.ENUM_FIELD)

        option_value_1 = OptionValue.objects.create(value="Type A")
        option_value_2 = OptionValue.objects.create(value="Type B")

        option_field.options.add(option_value_1)
        option_field.options.add(option_value_2)

        self.assertEqual(risk_type.risks.count(), 0)

        post_data = {
            "risk_type": risk_type.id,
            "values": [
                {
                    "field_id": text_field.id,
                    "value": "Hyundai"
                },
                {
                    "field_id": number_field.id,
                    "value": 123456,
                },
                {
                    "field_id": date_field.id,
                    "value": "1970-01-01"
                },
                {
                    "field_id": option_field.id,
                    "value": option_value_2.id
                },
            ]
        }

        response = self.client.post("/api/risks/", post_data, format="json")
        self.assertEqual(response.status_code, 201)

        self.assertEqual(risk_type.risks.count(), 1)

        created_risk = risk_type.risks.first()
        field_values = created_risk.field_values.all()

        text_field_value = field_values.get(field__field_type=Field.TEXT_FIELD)
        self.assertEqual(text_field_value.field.id, text_field.id)
        self.assertEqual(text_field_value.value, "Hyundai")

        number_field_value = field_values.get(field__field_type=Field.NUMBER_FIELD)  # NOQA
        self.assertEqual(number_field_value.field.id, number_field.id)
        self.assertEqual(number_field_value.value, 123456)

        date_field_value = field_values.get(field__field_type=Field.DATE_FIELD)
        self.assertEqual(date_field_value.field.id, date_field.id)
        self.assertEqual(str(date_field_value.value), "1970-01-01")

        option_field_value = field_values.get(field__field_type=Field.ENUM_FIELD)  # NOQA
        self.assertEqual(option_field_value.field.id, option_field.id)
        self.assertEqual(option_field_value.value.id, option_value_2.id)

    def test_risk_api_post_raises_validation_error_for_invalid_values(self):
        risk_type = RiskType.objects.create(name="Cars")

        Field.objects.create(name="Name", risk_type=risk_type,
                             field_type=Field.TEXT_FIELD)

        number_field = Field.objects.create(
            name="Model No.", risk_type=risk_type,
            field_type=Field.NUMBER_FIELD)

        date_field = Field.objects.create(
            name="Purchase date", risk_type=risk_type,
            field_type=Field.DATE_FIELD)

        option_field = Field.objects.create(
            name="Car Type", risk_type=risk_type,
            field_type=Field.ENUM_FIELD)

        option_value_1 = OptionValue.objects.create(value="Type A")
        option_value_2 = OptionValue.objects.create(value="Type B")

        option_field.options.add(option_value_1)
        option_field.options.add(option_value_2)

        self.assertEqual(risk_type.risks.count(), 0)

        post_data = {
            "risk_type": risk_type.id,
            "values": [
                {
                    "field_id": 0,  # A non-existent field
                    "value": "Some Text"
                },
                {
                    "field_id": number_field.id,
                    "value": "Definitely not a number",
                },
                {
                    "field_id": date_field.id,
                    "value": "Invalid date"
                },
                {
                    "field_id": option_field.id,
                    "value": 0  # A pk that does not exists
                },
            ]
        }

        response = self.client.post("/api/risks/", post_data, format="json")
        self.assertEqual(response.status_code, 400)

        expected_error_response = {
            "values": [
                {
                    "field_id": ['Invalid pk "0" - object does not exist.']
                },
                {
                    "value": ["A valid integer is required."],
                },
                {
                    "value": ["Date has wrong format. Use one of these formats"
                              " instead: YYYY-MM-DD."],
                },
                {
                    "value": ['Invalid value. Option value does not exist.']
                }
            ]
        }
        self.assertEqual(json.loads(response.content), expected_error_response)

    def test_risk_api_post_raises_validation_error_for_missing_fields(self):
        risk_type = RiskType.objects.create(name="Cars")

        text_field = Field.objects.create(name="Name", risk_type=risk_type,
                                          field_type=Field.TEXT_FIELD)

        Field.objects.create(name="Model No.", risk_type=risk_type,
                             field_type=Field.NUMBER_FIELD)

        self.assertEqual(risk_type.risks.count(), 0)

        post_data = {
            "risk_type": risk_type.id,
            "values": [
                {
                    "field_id": text_field.id,
                    "value": "Some Text"
                },
            ]
        }

        response = self.client.post("/api/risks/", post_data, format="json")
        self.assertEqual(response.status_code, 400)

        expected_error_response = {
            "non_field_errors": [
                "All fields are required. 'Model No.' fields not found."
            ]
        }
        self.assertEqual(json.loads(response.content), expected_error_response)

    def test_risk_api_post_raises_validation_error_for_duplicate_fields(self):
        risk_type = RiskType.objects.create(name="Cars")

        text_field = Field.objects.create(name="Name", risk_type=risk_type,
                                          field_type=Field.TEXT_FIELD)

        number_field = Field.objects.create(
            name="Model No.", risk_type=risk_type,
            field_type=Field.NUMBER_FIELD)

        self.assertEqual(risk_type.risks.count(), 0)

        post_data = {
            "risk_type": risk_type.id,
            "values": [
                {
                    "field_id": text_field.id,
                    "value": "Some Text"
                },
                {
                    "field_id": number_field.id,
                    "value": 12345,
                },
                {
                    "field_id": text_field.id,
                    "value": "Some more text"
                },
            ]
        }

        response = self.client.post("/api/risks/", post_data, format="json")
        self.assertEqual(response.status_code, 400)

        expected_error_response = {
            "non_field_errors": ["Duplicate fields are not allowed."]
        }
        self.assertEqual(json.loads(response.content), expected_error_response)
