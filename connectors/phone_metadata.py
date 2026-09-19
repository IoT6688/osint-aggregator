import phonenumbers

from phonenumbers import (
    carrier,
    geocoder,
    number_type,
)

from core.base_connector import (
    BaseConnector,
    ConnectorResult,
    TargetType,
)

from core.registry import registry


@registry.register
class PhoneMetadataConnector(BaseConnector):

    name = "phone_metadata"
    category = "phone"
    display_name = "Phone Number Metadata"
    accepted_target_types = [TargetType.PHONE]
    source = "Google libphonenumber"

    def validate_target(self, target: str) -> bool:
        target = target.strip()

        if not target:
            return False

        try:
            parsed = phonenumbers.parse(
                target,
                None
            )

            return phonenumbers.is_possible_number(parsed)

        except phonenumbers.NumberParseException:
            return False

    def fetch(self, target: str) -> ConnectorResult:

        target = target.strip()

        try:
            parsed = phonenumbers.parse(
                target,
                None
            )

            possible = phonenumbers.is_possible_number(parsed)
            valid = phonenumbers.is_valid_number(parsed)

            region_code = phonenumbers.region_code_for_number(parsed)

            country_code = parsed.country_code

            national_number = parsed.national_number

            number_type_value = number_type(parsed)

            number_type_name = {
                0: "FIXED_LINE",
                1: "MOBILE",
                2: "FIXED_LINE_OR_MOBILE",
                3: "TOLL_FREE",
                4: "PREMIUM_RATE",
                5: "SHARED_COST",
                6: "VOIP",
                7: "PERSONAL_NUMBER",
                8: "PAGER",
                9: "UAN",
                10: "VOICEMAIL",
                99: "UNKNOWN",
            }.get(
                number_type_value,
                "UNKNOWN"
            )

            location = geocoder.description_for_number(
                parsed,
                "en"
            )

            carrier_name = carrier.name_for_number(
                parsed,
                "en"
            )

            formatted_international = (
                phonenumbers.format_number(
                    parsed,
                    phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
            )

            formatted_national = (
                phonenumbers.format_number(
                    parsed,
                    phonenumbers.PhoneNumberFormat.NATIONAL
                )
            )

            raw_data = {
                "input": target,

                "country_code": country_code,

                "region_code": region_code,

                "national_number": str(
                    national_number
                ),

                "possible": possible,

                "valid": valid,

                "number_type": number_type_name,

                "location": location,

                "carrier": carrier_name,

                "formatted_international":
                    formatted_international,

                "formatted_national":
                    formatted_national,
            }

            return ConnectorResult(
                connector_name=self.name,
                display_name=self.display_name,
                source=self.source,
                status="ok",
                raw_data=raw_data,
            )

        except phonenumbers.NumberParseException as error:

            return self.error_result(
                f"Số điện thoại không hợp lệ: {error}"
            )

        except Exception as error:

            return self.error_result(
                f"Lỗi không xác định: {error}"
            )