import azure.durable_functions as df
from study import Study
from typing import List

find_mode_entities_blueprint = df.Blueprint()


# I want to turn the type of the input to a list of Study objects but run into
# serialization issues with Azure function
@find_mode_entities_blueprint.activity_trigger(input_name="studies")
def find_mode_entities(studies: List[any]) -> dict:

    possible_duration_values = {}
    possible_drug_or_compound_values = {}
    possible_route_of_administration_values = {}
    possible_internal_study_number_values = {}
    possible_external_study_number_values = {}
    possible_test_facility_values = {}

    mode_study = Study()

    for study in studies:
        count_property_value(study, "duration", possible_duration_values)
        count_property_value(
            study, "drug_or_compound", possible_drug_or_compound_values
        )
        count_property_value(
            study, "route_of_administration", possible_route_of_administration_values
        )
        count_property_value(
            study, "internal_study_number", possible_internal_study_number_values
        )
        count_property_value(
            study, "external_study_number", possible_external_study_number_values
        )
        count_property_value(study, "test_facility", possible_test_facility_values)
        # we won't calculate mode for stakeholders, significant_dates, or species
        # as these are lists where you might find valid unique entries
        # throughout the original document, so instead we aggregate list results
        try_append_values(study, "stakeholders", mode_study.stakeholders)
        try_append_values(study, "significant_dates", mode_study.significant_dates)
        try_append_values(study, "species", mode_study.species)

    mode_study.duration = try_get_mode_value(possible_duration_values)
    mode_study.drug_or_compound = try_get_mode_value(possible_drug_or_compound_values)
    mode_study.route_of_administration = try_get_mode_value(
        possible_route_of_administration_values
    )
    mode_study.internal_study_number = try_get_mode_value(
        possible_internal_study_number_values
    )
    mode_study.external_study_number = try_get_mode_value(
        possible_external_study_number_values
    )
    mode_study.test_facility = try_get_mode_value(possible_test_facility_values)

    return {
        "duration": mode_study.duration,
        "species": mode_study.species,
        "drug_or_compound": mode_study.drug_or_compound,
        "route_of_administration": mode_study.route_of_administration,
        "internal_study_number": mode_study.internal_study_number,
        "external_study_number": mode_study.external_study_number,
        "test_facility": mode_study.test_facility,
        "stakeholders": mode_study.stakeholders,
        "significant_dates": mode_study.significant_dates,
    }


# seems like python is passing by reference so we don't need to return the collection
def count_property_value(object, property_key, values_collection):
    try:
        value = object[property_key]

        # skip None values, not every chunk will find enough data to support a good guess
        if value is None:
            return

        if value in values_collection:
            values_collection[value] += 1
        else:
            values_collection[value] = 1
    except KeyError or AttributeError:
        pass
    # we'll ignore ones we can't read for now


def try_append_values(object, property_key, values_collection):
    try:
        additional_values = object[property_key]
        if (
            isinstance(additional_values, list)
            and isinstance(values_collection, list)
            and len(additional_values) > 0
        ):
            for val in additional_values:
                values_collection.append(val)
    except (KeyError, AttributeError):
        pass
    # we'll ignore ones we can't read for now


def try_get_mode_value(values_collection):
    try:
        mode_val = max(values_collection, key=values_collection.get)
        return mode_val
    except (AttributeError, ValueError, TypeError, KeyError):
        return None
    # we'll ignore ones we can't read for now
