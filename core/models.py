from django.db import models


class RiskType(models.Model):
    """
    A data model which is used to create a `Risk`.

    A RiskType defines all the fields required to be filled/suppied while
    creating a Risk object.

    E.g. A "Car" risk type can have fields like "Owner name", "Model No.",
    "Purchase Date" etc which are then required to be filled by while
    creating a Risk instance.
    """
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Risk(models.Model):
    """
    Data collected on a risk of a given RiskType.
    """
    risk_type = models.ForeignKey(RiskType, related_name="risks",
                                  on_delete=models.CASCADE)

    def __str__(self):
        return self.risk_type.name


class OptionValue(models.Model):
    value = models.TextField()

    def __str__(self):
        return self.value


class Field(models.Model):
    """
    Model to store data on field for a given RiskType.

    This essentially defines the data type of a field created by user.
    If the field type is "enum", a list of possible "options" are required.
    """

    TEXT_FIELD = "text"
    NUMBER_FIELD = "number"
    DATE_FIELD = "date"
    ENUM_FIELD = "enum"

    FIELD_TYPE_CHOICES = (
        (TEXT_FIELD, "Text"),
        (NUMBER_FIELD, "Number"),
        (DATE_FIELD, "Date"),
        (ENUM_FIELD, "Enum"),
    )

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    risk_type = models.ForeignKey(RiskType, related_name="fields",
                                  on_delete=models.CASCADE)

    field_type = models.CharField(max_length=10, choices=FIELD_TYPE_CHOICES)
    options = models.ManyToManyField(OptionValue, blank=True)

    def __str__(self):
        return self.name


class FieldValue(models.Model):
    """
    Data collected for a field in a given risk.

    Each type of data, depending on the field type is store on a separate
    field/column.

    A generic "value" attribute is used to represent and populate any type
    of data for simplicity.
    """
    field = models.ForeignKey(Field, related_name="field_values",
                              on_delete=models.CASCADE)
    risk = models.ForeignKey(Risk, related_name="field_values",
                             on_delete=models.CASCADE)

    value_text = models.TextField(blank=True, null=True)
    value_number = models.IntegerField(blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)
    value_option = models.ForeignKey(OptionValue,
                                     related_name="field_values",
                                     on_delete=models.CASCADE,
                                     null=True, blank=True)

    def __str__(self):
        return self.value

    @property
    def value(self):
        """
        Get value for field based on the field type.
        """
        value_map = {
            Field.TEXT_FIELD: self.value_text,
            Field.NUMBER_FIELD: self.value_number,
            Field.DATE_FIELD: self.value_date,
            Field.ENUM_FIELD: self.value_option,
        }
        return value_map[self.field.field_type]

    @value.setter
    def value(self, data):
        """
        Set value for field based on field type.
        Assumes that the `data` is a valid object for corresponding field type.

        For e.g. A string object for field type "text" or a "OptionValue"
        object for field type "enum".
        """
        attr_map = {
            Field.TEXT_FIELD: "value_text",
            Field.NUMBER_FIELD: "value_number",
            Field.DATE_FIELD: "value_date",
            Field.ENUM_FIELD: "value_option",
        }
        setattr(self, attr_map[self.field.field_type], data)
