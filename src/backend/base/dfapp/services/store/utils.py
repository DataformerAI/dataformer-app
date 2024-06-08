from typing import TYPE_CHECKING, List

import httpx

if TYPE_CHECKING:
    from dfapp.services.store.schema import ListComponentResponse
    from dfapp.services.store.service import StoreService


def process_tags_for_post(component_dict):
    tags = component_dict.pop("tags", None)
    if tags and all(isinstance(tag, str) for tag in tags):
        component_dict["tags"] = [{"tags_id": tag} for tag in tags]
    return component_dict


async def update_components_with_user_data(
    components: List["ListComponentResponse"],
    store_service: "StoreService",
    store_api_key: str,
    liked: bool,
):
    """
    Updates the components with the user data (liked_by_user and in_users_collection)
    """
    component_ids = [str(component.id) for component in components]
    if liked:
        # If liked is True, this means all we got were liked_by_user components
        # So we can set liked_by_user to True for all components
        liked_by_user_ids = component_ids
    else:
        liked_by_user_ids = await store_service.get_liked_by_user_components(
            component_ids=component_ids,
            api_key=store_api_key,
        )
    # Now we need to set the liked_by_user attribute
    for component in components:
        component.liked_by_user = str(component.id) in liked_by_user_ids

    return components


# Get the latest released version of dfapp (https://pypi.org/project/dfapp/)
def get_lf_version_from_pypi():
    try:
        response = httpx.get("https://pypi.org/pypi/dfapp/json")
        if response.status_code != 200:
            return None
        return response.json()["info"]["version"]
    except Exception:
        return None


def process_component_data(nodes_list):
    names = [node["id"].split("-")[0] for node in nodes_list]
    metadata = {}
    for name in names:
        if name in metadata:
            metadata[name]["count"] += 1
        else:
            metadata[name] = {"count": 1}
    metadata["total"] = len(names)

    return metadata
