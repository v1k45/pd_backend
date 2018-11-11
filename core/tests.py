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

    def test_risk_type_api_put_works_with_valid_data(self):
        post_data = {
            "name": "Sample Risk Type",
            "fields": [
                {"name": "Field Name", "field_type": "text"}
            ]
        }
        response = self.client.post("/api/risk_types/", post_data,
                                    format="json")
        self.assertEqual(response.status_code, 201)

        self.assertEqual(RiskType.objects.count(), 1)
        risk_type = RiskType.objects.first()
        self.assertIsNotNone(risk_type)
        self.assertEqual(risk_type.name, post_data["name"])

        update_data = {
            "name": "Updated Risk Type",
            "description": "Updated description",
            "fields": [
                {"name": "Field Name", "field_type": "text"}
            ]
        }

        response = self.client.put("/api/risk_types/%s/" % risk_type.id,
                                   update_data, format="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(RiskType.objects.count(), 1)
        risk_type = RiskType.objects.first()
        self.assertIsNotNone(risk_type)
        self.assertEqual(risk_type.name, update_data["name"])
