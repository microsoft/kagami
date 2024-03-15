import azure.durable_functions as df
from langchain_core.documents import Document
from kernel_factory import KernelFactory
import semantic_kernel as sk
import json, logging, time

from study import Study

import tiktoken

extract_entities_blueprint = df.Blueprint()


@extract_entities_blueprint.activity_trigger(input_name="chunk")
async def extract_entities(chunk: Document) -> Study:
    cl100k_base = tiktoken.get_encoding("cl100k_base")
    tokens = len(cl100k_base.encode(chunk))
    start_time = time.time()

    kernel = KernelFactory.create_kernel()

    multi_entity_result = await kernel.invoke(
        kernel.plugins["EntityExtraction"]["ExtractMultipleEntities"],
        sk.KernelArguments(input=chunk),
    )

    stakeholders_result = await kernel.invoke(
        kernel.plugins["EntityExtraction"]["ExtractStakeholders"],
        sk.KernelArguments(input=chunk),
    )

    dates_result = await kernel.invoke(
        kernel.plugins["EntityExtraction"]["ExtractSignificantDates"],
        sk.KernelArguments(input=chunk),
    )

    # attempt to load from json
    study = Study()
    try:
        study = Study(multi_entity_result.value[0].content)
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        pass

    try:
        # this needs better consistent json output before refining the parsing
        name_list = json.loads(stakeholders_result.value[0].content)
        study.stakeholders = [entry["name"] for entry in name_list]
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        pass

    try:
        # this needs better consistent json output before refining the parsing
        date_list = json.loads(dates_result.value[0].content)
        study.significant_dates = [entry["date"] for entry in date_list]
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        pass
    
    # considering following lines negligible to performance and thus out of scope for measurement
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"extract_entities took {elapsed_time} seconds for a {tokens} token chunk.")

    # not sure why im having such difficulty serializing this for passing between functions
    return {
        "duration": study.duration,
        "species": study.species,
        "drug_or_compound": study.drug_or_compound,
        "route_of_administration": study.route_of_administration,
        "internal_study_number": study.internal_study_number,
        "external_study_number": study.external_study_number,
        "test_facility": study.test_facility,
        "stakeholders": study.stakeholders,
        "significant_dates": study.significant_dates
    }
