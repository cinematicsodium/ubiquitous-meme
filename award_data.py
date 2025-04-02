import unicodedata
from dataclasses import dataclass
from formatter import Formatter
from pathlib import Path
from typing import Optional

import fitz
import yaml
from rich.traceback import install

install(show_locals=True)


@dataclass
class AwardData:
    log_id: str = ""
    employee_name: str = "employee_name"
    _monetary_amount: str = ""
    _time_off_amount: str = ""
    employee_org: str = "organization"
    employee_pay_plan: str = "pay_plan_gradestep_1"
    sas_monetary_amount: str = "undefined"
    sas_time_off_amount: str = "hours_2"
    ots_monetary_amount: str = "on_the_spot_award"
    ots_time_off_amount: str = "hours"
    nominator_name: str = "please_print"
    nominator_org: str = "org"
    certfier_name: str = "special_act_award_funding_string_2"
    certifier_org: str = "org_2"
    supervisor_name: str = "please_print_2"
    supervisor_org: str = "org_3"
    approver_name: str = "please_print_3"
    approver_org: str = "org_4"
    administrator_name: str = "please_print_4"
    reviewer_name: str = "please_print_5"
    funding_string: str = "special_act_award_funding_string_1"
    justification: str = "extent_of_application"
    _value: str = ""
    _extent: str = ""
    _type: str = ""
    _category: str = "IND"
    _pdf_data: dict[str, Optional[str]] = None

    def extract(self, pdf_path: Path) -> dict[str, Optional[str]]:
        """Extracts the data from the PDF file using PyMuPDF."""
        data = {}
        with fitz.open(pdf_path) as doc:
            for page in doc:
                for field in page.widgets():
                    key = Formatter(field.field_name).key()
                    val = Formatter(field.field_value).value()
                    self._pdf_data[key] = val

    def populate(self):
        for field_name, placeholder_value in self.__dict__.items():
            if field_name.startswith("_"):
                continue
            field_value = self._pdf_data.get(placeholder_value)
            self.__setattr__(field_name, field_value)

    def assign_type(self):
        sas_fields = [
            "sas_monetary_amount",
            "sas_time_off_amount",
        ]

        if sas_fields:
            self._type = "SAS"
            self._monetary_amount = self.sas_monetary_amount
            self._time_off_amount = self.sas_time_off_amount

        else:
            self._type = "OTS"
            self._monetary_amount = self.ots_monetary_amount
            self._time_off_amount = self.ots_time_off_amount

    def format_fields(self):
        name_fields = [
            "employee_name",
            "nominator_name",
            "certfier_name",
            "supervisor_name",
            "approver_name",
            "administrator_name",
            "reviewer_name",
        ]
        numerical_fields = ["monetary_amount", "time_off_amount"]
        for k, v in self.__dict__.items():
            if k in name_fields:
                v = Formatter(v).name()
            elif k in numerical_fields:
                v = Formatter(v).numerical()
            elif k == "reason":
                v = Formatter(v).reason()
            else:
                continue
            self.__dict__[k] = v

    def identify_missing(self) -> list[str]:
        fields_required: list[str] = [
            "employee_name",
            "nominator_name",
            "supervisor_name",
            "approver_name",
            "certifier_name",
            "reviewer_name",
            "justification",
        ]
        fields_missing: list[str] = [
            k for k, v in self.__dict__.items() if k in fields_required and not v
        ]
        return fields_missing

    def missing_str(self) -> str:
        mfields = yaml.safe_dump(self.identify_missing(), indent=4)
        return f"Missing Fields:\n{mfields}"

    def is_incomplete(self) -> bool:
        return False if len(self.identify_missing()) == 0 else True

    def items(self) -> str:
        self._assign_type()
        self._format_fields()
        padding: int = max(len(k) for k in self.__dict__.keys()) + 4
        fields_to_ignore = [
            "sas_monetary_amount",
            "sas_time_off_amount",
            "ots_monetary_amount",
            "ots_time_off_amount",
            "administrator_name",
        ]

        string: str = ""
        for k, v in self.__dict__.items():
            if k == "reason":
                word_count = len(self.justification.split())
                v = f"{word_count} words"
            # elif k in fields_to_ignore:
            #     continue
            if not v:
                v = "-"
            k = f"{k}:".ljust(padding)
            string += f"{k}{v}\n"
        return string.strip()
