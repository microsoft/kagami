import azure.durable_functions as df
from langchain_core.documents import Document
from kernel_factory import KernelFactory
import semantic_kernel as sk

extract_entities_blueprint = df.Blueprint()


@extract_entities_blueprint.activity_trigger(input_name="chunks")
async def extract_entities(chunk: Document) -> dict:
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

    return {
        "multi_entity_result": multi_entity_result.value[0].content,
        "stakeholders_result": stakeholders_result.value[0].content,
        "dates_result": dates_result.value[0].content,
    }
