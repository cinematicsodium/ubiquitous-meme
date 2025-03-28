from pathlib import Path

import fitz
from rich.traceback import install
from UTILS import Formatting, LogID
from indFields import config0
from pdfConfigs import ConfigIND

install(show_locals=True)




def extract_data(pdf_path: Path) -> dict[str, str]:
    pdf_data: dict[str, str] = {}
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            for field in page.widgets():
                field_name = Formatting.pdf_object(
                    key=str(field.field_name)
                )
                field_value = Formatting.pdf_object(
                    val = str(field.field_value)
                )
                while field_name in pdf_data.keys():
                    n = 1
                    x = str(n).zfill(3)
                    field_name = f"{field_name}_{x}"
                pdf_data[field_name] = field_value
    return pdf_data


def get_selection(options_list: list[str], pdf_data: dict[str, str]) -> str:
    selections = [sel for sel in options_list if str(pdf_data.get(sel)).lower() == "on"]
    if not selections:
        return ""
    elif len(selections) == 1:
        return selections[0]
    elif len(selections) > 1:
        return "multiple_values_selected"


def get_value_and_extent(pdf_data: dict[str, str]) -> str:
    value_options = ["moderate", "high", "exceptional"]
    extent_options = ["limited", "extended", "general"]
    value = get_selection(value_options, pdf_data)
    extent = get_selection(extent_options, pdf_data)
    return value, extent




def process(pdf_data: dict[str, str]):
    value, extent = get_value_and_extent(pdf_data)
    log_id = LogID.get()

    ind_award: ConfigIND = ConfigIND(
        value=value, extent=extent, log_id=f"25-IND-{log_id}"
    )

    field_names = list(pdf_data.keys())
    if field_names == config0:
        ind_award.employee_pay_plan = "pay_plan_gradestep"
        ind_award.sas_monetary_amount = "amount"
        ind_award.nominator_name = "nominators_name"
        ind_award.nominator_org = "organization_2"
        ind_award.supervisor_name = "a_nominees_team_leadersupervisor_1"
        ind_award.supervisor_org = "organization_3"
        ind_award.approver_name = "approving_officialdesignee_1"
        ind_award.approver_org = "organization_5"
        ind_award.certfier_name = "compliance_review_completed_by_1"
        ind_award.certifier_org = "organization_6"
        ind_award.justification = "extent_of_application_limited_extended_or_general"

    ind_award.populate_fields(pdf_data)
    if ind_award.is_incomplete():
        print(ind_award.missing_fields_string())
    else:
        print(ind_award.items())
    LogID.update()


def main():
    files: Path
    for file in files.iterdir():
        print(f'\n\n{file.name}\n')
        pdf_data = extract_data(file)
        process(pdf_data)


main()
