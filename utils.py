import yaml
from typing import Optional
import unicodedata
from winsound import Beep


class LogID:
    def get(type: str = "IND") -> str:
        try:
            with open("log_id.yaml", "r") as yfile:
                award_id_data: dict[str, int] = yaml.safe_load(yfile)
                if not award_id_data:
                    raise ValueError("Award ID data not found.")
        except FileNotFoundError:
            raise FileNotFoundError("log_id.yaml file not found.")

        award_id = str(award_id_data.get(type.upper()))
        if not award_id:
            raise ValueError(f"{type} ID not found.")

        return award_id.zfill(3)

    @staticmethod
    def update(type: str = "IND") -> str:
        try:
            with open("log_id.yaml", "r+") as yfile:
                award_id_data: dict[str, int] = yaml.safe_load(yfile)
                if not award_id_data:
                    raise ValueError("Award ID data not found.")
                elif not award_id_data.get(type):
                    raise ValueError(f"{type} ID data not found")
                elif not isinstance(award_id_data[type], int):
                    raise ValueError(f"{type} ID is not an integer.")
                else:
                    award_id_data[type] += 1
                    yfile.seek(0)
                    yaml.safe_dump(award_id_data, yfile, indent=4)
                    yfile.truncate()
        except FileNotFoundError:
            raise FileNotFoundError("log_id.yaml file not found.")


class Formatting:
    TITLES = {
        "Dr.",
        "Mr.",
        "Mrs.",
        "Miss.",
        "Ms.",
        "Prof.",
        "Ph.D",
        "Dr",
        "Mr",
        "Mrs",
        "Miss",
        "Ms",
        "Prof",
        "PhD",
    }

    def __name_parts__(raw_name: str) -> str:
        return [
            name_part.strip()
            for name_part in raw_name.split()
            if name_part
            and name_part not in Formatting.TITLES
            and not (
                (
                    name_part.startswith('"') and name_part.endswith('"')
                )  # ['John', '"Johnny"', 'Public']
                or (
                    name_part.startswith("(") and name_part.endswith(")")
                )  # ['John', '(Johnny)', 'Public']
                or (
                    len(name_part) == 3 and name_part.endswith(".")
                )  # titles that may not be included in Formatting.TITLES
                or (
                    len(name_part) == 2 and name_part.endswith(".")
                )  # ['John', 'Q.', 'Public'] or ['J.', 'Public']
                or (
                    len(name_part) == 1
                )  # ['John', 'Q', 'Public'] or ['J', 'Public'] or ['John', 'P']
            )
        ]

    @staticmethod
    def justification(field_text: str) -> str:
        if not field_text:
            return ""

        field_text = field_text.replace('"', "'")
        return f'"{field_text}"'

    def __input__(original_name: str) -> str:
        frequency_hz: int = 1000
        duration_ms: int = 500
        try:
            Beep(frequency_hz, duration_ms)
        except RuntimeError as e:
            print(e)

        max_attempts: int = 3
        for _ in range(max_attempts):
            print(
                f'Enter "{original_name}" formatted as "FIRST LAST"\n'
                "Enter 0 to skip."
            )
            user_input: str = input(">>> ").strip()
            print()

            if user_input == "0":
                raise ValueError(f"Name not recognized: {original_name}")

            split_name: list[str] = user_input.split()
            if len(split_name) == 2:
                first_name, last_name = split_name
                return last_name, first_name

            print("Invalid name format.\n")

        raise ValueError(f"Invalid name format: {original_name}")

    @staticmethod
    def name(raw_name: str) -> str:
        if not raw_name:
            return
        name_parts: list[str] = Formatting.__name_parts__(raw_name)

        last_name, first_name = "", ""

        if len(name_parts) == 2:
            if "," in name_parts[0]:  # name_parts = ['Public,', 'John']
                last_name, first_name = name_parts[0].replace(",", ""), name_parts[1]
            else:
                last_name, first_name = (
                    name_parts[1],
                    name_parts[0],
                )  # not ['J.','Public'] or ['John', 'P.']

        elif len(name_parts) == 3:
            min_len: int = min(len(name_part) for name_part in name_parts)
            contains_prd: bool = any("." in name_part for name_part in name_parts)
            if min_len >= 3 and not contains_prd:
                last_name, first_name = name_parts[2], name_parts[0]

        if not all([last_name, first_name]):
            return raw_name
            # last_name, first_name = Formatting.__input__(raw_name)

        return ", ".join([last_name, first_name]).title()

    @staticmethod
    def numerical(field_text: str) -> float:
        if not field_text:
            return 0.0
        digits = "".join(c for c in field_text if c.isdigit() or c == ".")
        try:
            return float(digits) if digits else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def __reduce_blank_chars__(text: Optional[str]) -> str:
        if text is None:
            return
        text = str(text) if text != str(text) else text
        if "\n" in text:
            parts = text.split("\n")
            text = "\n".join(f"> {part}" for part in parts if part)
        if " " in text:
            parts = text.split(" ")
            text = " ".join(part for part in parts if part)
        return unicodedata.normalize("NFKD", text).strip()

    @staticmethod
    def pdf_object(
        key: Optional[str] = None, val: Optional[str] = None
    ) -> Optional[str]:
        if key is None and val is None:
            raise ValueError

        if key is not None:
            key = (
                Formatting.__reduce_blank_chars__(key).lower().replace(" ", "_").strip()
            )

        if val is not None:
            val = Formatting.__reduce_blank_chars__(val)
            val = val if val else None
        return (key, val) if key and val else key if key else val
