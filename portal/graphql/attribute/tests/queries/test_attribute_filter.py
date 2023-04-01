import graphene
import pytest

from portal.graphql.tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db


ATTRIBUTES_FILTER_QUERY = """
    query($filters: AttributeFilterInput!) {
      attributes(first: 10, filter: $filters) {
        edges {
          node {
            name
            slug
          }
        }
      }
    }
"""

ATTRIBUTES_VALUE_FILTER_QUERY = """
query($filters: AttributeValueFilterInput!) {
    attributes(first: 10) {
        edges {
            node {
                name
                slug
                choices(first: 10, filter: $filters) {
                    edges {
                        node {
                            name
                            slug
                        }
                    }
                }
            }
        }
    }
}
"""


def test_search_attributes(api_client, color_attribute, size_attribute):
    variables = {"filters": {"search": "color"}}

    attributes = get_graphql_content(
        api_client.post_graphql(ATTRIBUTES_FILTER_QUERY, variables)
    )["data"]["attributes"]["edges"]

    assert len(attributes) == 1
    assert attributes[0]["node"]["slug"] == "color"


@pytest.mark.parametrize(
    "filter_value",
    ["red", "blue"],
)
def test_search_attributes_value(
    filter_value, api_client, color_attribute, size_attribute
):
    variables = {"filters": {"search": filter_value}}

    attributes = get_graphql_content(
        api_client.post_graphql(ATTRIBUTES_VALUE_FILTER_QUERY, variables)
    )
    values = attributes["data"]["attributes"]["edges"][0]["node"]["choices"]["edges"]
    assert len(values) == 1
    assert values[0]["node"]["slug"] == filter_value


def test_filter_attributes_if_filterable_in_dashboard(
    api_client, color_attribute, size_attribute
):
    color_attribute.filterable_in_dashboard = False
    color_attribute.save(update_fields=["filterable_in_dashboard"])

    variables = {"filters": {"filterableInDashboard": True}}

    attributes = get_graphql_content(
        api_client.post_graphql(ATTRIBUTES_FILTER_QUERY, variables)
    )["data"]["attributes"]["edges"]

    assert len(attributes) == 1
    assert attributes[0]["node"]["slug"] == "size"
