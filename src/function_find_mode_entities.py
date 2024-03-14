import azure.durable_functions as df
import json, os
from typing import List

find_mode_entities_blueprint = df.Blueprint()


@find_mode_entities_blueprint.activity_trigger(input_name="allExtractedEntities")
def find_mode_entities(allExtractedEntities) -> dict:
    # : List[dict]
    # what is type of input?
    calculated_mode_response = calculate_mode_response(allExtractedEntities)
    return calculated_mode_response


def calculate_mode_response(list_of_json_objects, printObjs=False):
    if len(list_of_json_objects) == 0:
        return None

    # remove any None objects from the list
    list_of_json_objects = [val for val in list_of_json_objects if val is not None]

    if printObjs:
        print("List of JSON Objects: ", list_of_json_objects)

    first_entry = list_of_json_objects[0]
    # hacky conversion of other types to dictionary for keys
    schema = (
        json.loads(first_entry)
        if isinstance(first_entry, str)
        else json.loads(json.dumps(first_entry))
    )

    if printObjs:
        print("Schema: ", schema)

    property_keys = schema.keys()

    mode_response = {}
    responses = {}

    for key in property_keys:
        if printObjs:
            print("Beginning loop for key: ", key)
        for obj in list_of_json_objects:
            if printObjs:
                print("Evaluating: ", obj)

            # hacky conversion of other types to dictionary for keysl see above
            json_obj = (
                json.loads(obj) if isinstance(obj, str) else json.loads(json.dumps(obj))
            )

            flatten_json(json_obj)
            if isinstance(obj, list):
                print(
                    f"{obj} is a list in {list_of_json_objects}", list_of_json_objects
                )

            value = json_obj[key]

            # todo: determine how to handle list values, for now skipping to prepare for demo

            if isinstance(value, list):
                continue

            if json_obj[key] in responses:
                responses[value] += 1
            else:
                responses[value] = 1

        if len(responses) > 0:
            mode_response[key] = max(responses, key=responses.get)
        responses = {}
    return mode_response


def flatten_list_of_list_strings(original_list):
    list_of_lists = [json.loads(val) for val in original_list if val is not None]
    return [val for sublist in list_of_lists for val in sublist]


def flatten_json(json_obj):
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(json_obj)
    return out
