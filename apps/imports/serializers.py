from rest_framework import serializers

from .models import ImportBatch, RawExcelRow


class RawExcelRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawExcelRow
        fields = ("id", "row_index", "raw_data")


class ImportBatchSerializer(serializers.ModelSerializer):
    rows = RawExcelRowSerializer(many=True, read_only=True)

    class Meta:
        model = ImportBatch
        fields = (
            "id",
            "created_at",
            "uploaded_by",
            "source_file_name",
            "source_file",
            "status",
            "error_message",
            "rows",
        )
        read_only_fields = ("uploaded_by", "status", "error_message", "source_file_name")

    def create(self, validated_data):
        source_file = validated_data.get("source_file")
        if source_file is not None:
            validated_data["source_file_name"] = source_file.name
        return super().create(validated_data)

    def validate(self, attrs):
        if self.instance is None and not attrs.get("source_file"):
            raise serializers.ValidationError({"source_file": "Excel file is required"})
        return attrs
