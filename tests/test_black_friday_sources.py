"""Tests for the Black Friday trend aggregation tool."""

import sys
from pathlib import Path

# Ensure project root on path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.black_friday_sources import BlackFridaySourcesTool


class TestBlackFridaySourcesTool:
    """Validate field coverage for BlackFridaySourcesTool outputs."""

    def setup_method(self) -> None:
        self.tool = BlackFridaySourcesTool()

    def test_fetch_trends_contains_required_fields(self):
        """Every trend sample should expose the mandatory fields."""

        records = self.tool.fetch_trends(limit=6)
        assert records, "Expected at least one trend record"

        required_fields = {
            "product_name",
            "platform",
            "category",
            "historical_peak_years",
            "target_audience",
            "price_range",
            "traction_signals",
            "source_url",
            "notes",
        }

        for payload in records:
            missing = required_fields - payload.keys()
            assert not missing, f"Missing fields: {missing}"
            assert payload["product_name"], "product name should not be empty"
            assert (
                isinstance(payload["historical_peak_years"], list)
                and payload["historical_peak_years"]
            ), "historical_peak_years should be a non-empty list"
            assert all(
                isinstance(year, int) for year in payload["historical_peak_years"]
            ), "all historical years must be integers"
            assert (
                isinstance(payload["target_audience"], list)
                and payload["target_audience"]
            ), "target audience should contain at least one segment"
            assert (
                isinstance(payload["price_range"], dict)
                and payload["price_range"]
            ), "price_range should be a populated dict"
            assert {
                "currency",
                "min",
                "max",
            }.issubset(payload["price_range"].keys()), "price_range must expose currency/min/max"
            assert payload["price_range"]["currency"], "currency should not be blank"
            assert (
                payload["price_range"]["min"]
                <= payload["price_range"]["max"]
            ), "price range min must be <= max"
            assert (
                isinstance(payload["traction_signals"], dict)
                and payload["traction_signals"]
            ), "traction_signals should contain at least one metric"

        platforms = {record["platform"] for record in records}
        assert platforms <= set(self.tool.supported_platforms)

    def test_fetch_trends_filters_category(self):
        """Category filters should narrow down the dataset."""

        kitchen_records = self.tool.fetch_trends(category="kitchen")
        assert kitchen_records, "Expected kitchen records"
        assert all(record["category"].lower() == "kitchen" for record in kitchen_records)

    def test_fetch_trends_drop_platform_field(self):
        """Consumers can optionally hide platform field."""

        records = self.tool.fetch_trends(include_platform_field=False)
        assert records, "Expected records when excluding platform field"
        assert all("platform" not in record for record in records)

    def test_fetch_trends_invalid_platform(self):
        """Unsupported platform requests should raise helpful errors."""

        try:
            self.tool.fetch_trends(platform="pinterest")
        except ValueError as exc:  # pragma: no cover - guard path
            assert "Unsupported platform" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("ValueError expected for unsupported platform")
