from dataclasses import dataclass
import json
import yaml
import unicodedata
from UTILS import Formatting


@dataclass
class ConfigIND:
    log_id: str = ""
    employee_name: str = "employee_name"
    monetary_amount: str = ""
    time_off_amount: str = ""
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
    value: str = ""
    extent: str = ""
    type: str = ""
    category: str = "IND"

    def __settype__(self):
        sas_fields = [
            "sas_monetary_amount",
            "sas_time_off_amount",
        ]

        if sas_fields:
            self.type = "SAS"
            self.monetary_amount = self.sas_monetary_amount
            self.time_off_amount = self.sas_time_off_amount

        else:
            self.type = "OTS"
            self.monetary_amount = self.ots_monetary_amount
            self.time_off_amount = self.ots_time_off_amount

    def __format_items__(self):
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
                v = Formatting.name(v)
            elif k in numerical_fields:
                v = Formatting.numerical(v)
            elif k == "justification":
                v = Formatting.justification(v)
            else:
                continue
            self.__dict__[k] = v
        if self.monetary_amount:
            self.monetary_amount = f"${int(self.monetary_amount)}"
        if self.time_off_amount:
            self.time_off_amount = f"{int(self.time_off_amount)} hours"

    def populate_fields(self, pdf_data: dict):
        for field_name, placeholder_value in self.__dict__.items():
            if field_name in [
                "value",
                "extent",
                "log_id",
                "type",
                "monetary_amount",
                "time_off_amount",
                "type",
                "category",
            ]:
                continue
            field_value = pdf_data.get(placeholder_value)
            if field_value:
                field_value = unicodedata.normalize("NFKD", field_value)
            else:
                field_value = None
            self.__setattr__(field_name, field_value)
        self.__settype__()

    def missing_fields(self) -> list[str]:
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

    def missing_fields_string(self) -> str:
        # mfields = json.dumps(self.missing_fields(), indent=4)
        mfields = yaml.safe_dump(self.missing_fields(), indent=4)
        return f"Missing Fields:\n{mfields}"

    def is_incomplete(self) -> bool:
        return False if len(self.missing_fields()) == 0 else True

    def items(self) -> str:
        self.__settype__()
        self.__format_items__()
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
            if k == "justification":
                word_count = len(self.justification.split())
                v = f"{word_count} words"
            elif k in fields_to_ignore:
                continue
            if v is None:
                v = "-"
            k = f"{k}:".ljust(padding)
            string += f"{k}{v}\n"
        return string
