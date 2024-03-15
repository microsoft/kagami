import json
from typing import List

class Study:
    def __init__(self, json_str=None) -> None:
        if json_str:
            json_dict = json.loads(json_str)
            self.duration: any = json_dict.get("Duration") or None
            self.species: List[any] = json_dict.get("Species") or []
            self.drug_or_compound: str = json_dict.get("DrugOrCompound") or None
            self.route_of_administration: str = json_dict.get("RouteOfAdministration") or None
            self.internal_study_number: str = json_dict.get("InternalStudyNumber") or None
            self.external_study_number: str = json_dict.get("ExternalStudyNumber") or None
            self.test_facility: str = json_dict.get("TestFacility") or None
        else:
            # Initialize with default values when json_str is None or empty
            self.duration = None
            self.species = []
            self.drug_or_compound = None
            self.route_of_administration = None
            self.internal_study_number = None
            self.external_study_number = None
            self.test_facility = None

        # Initialize other attributes
        self.stakeholders: List[str] = []
        self.significant_dates: List[str] = []


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
