import graphene
import pytest

from portal.graphql.tests.utils import get_graphql_content

pytestmark = pytest.mark.django_db

QUERY_INVESTMENT = """
    query Investment($id: ID, $month: Int, $year: Int) {
        investment(id: $id, month: $month, year: $year) {
            id
            month
            year
            isPublished
            channel{
                id
                name
            }
            items{
                id
                name
                value
            }
        }
    }
"""

QUERY_INVESTMENTS = """
    query Investments($first: Int, $channel: String, $filter: InvestmentFilterInput){
        investments(first: $first, channel: $channel, filter: $filter){
            edges{
                node{
                    id
                    month
                    year
                    channel{
                        id
                        name
                    }
                    items{
                        id
                        name
                        value
                    }
                }
            }
        }
    }
"""


def test_investment_staff_query_by_id(staff_api_client, investment):
    variables = {
        "id": graphene.Node.to_global_id("Investment", investment.pk),
    }
    response = staff_api_client.post_graphql(QUERY_INVESTMENT, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["investment"]

    assert data["month"] == investment.month
    assert data["year"] == investment.year


def test_investment_query_by_invalid_id(staff_api_client):
    investment_id = "'"
    variables = {"id": investment_id}
    response = staff_api_client.post_graphql(QUERY_INVESTMENT, variables=variables)
    content = get_graphql_content(response, ignore_errors=True)
    assert len(content["errors"]) == 1
    assert content["errors"][0]["message"] == f"Couldn't resolve id: {investment_id}."
    assert content["data"]["investment"] is None


def test_investment_staff_query_by_month_and_year(staff_api_client, investment):
    variables = {
        "month": investment.month,
        "year": investment.year,
    }
    response = staff_api_client.post_graphql(QUERY_INVESTMENT, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["investment"]

    assert data["month"] == investment.month
    assert data["year"] == investment.year


def test_investment_anonymouns_query_unpublished(api_client, investment):
    variables = {
        "id": graphene.Node.to_global_id("Investment", investment.pk),
    }
    response = api_client.post_graphql(QUERY_INVESTMENT, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["investment"]

    assert data is None


def test_investment_anonymouns_query_published(api_client, published_investment):
    variables = {
        "id": graphene.Node.to_global_id("Investment", published_investment.pk),
    }
    response = api_client.post_graphql(QUERY_INVESTMENT, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["investment"]

    assert data["month"] == published_investment.month
    assert data["year"] == published_investment.year


def test_investments_anonymouns_query(api_client, investment, published_investment):
    variables = {"first": 10}
    response = api_client.post_graphql(QUERY_INVESTMENTS, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["investments"]
    global_id = graphene.Node.to_global_id("Investment", published_investment.pk)

    assert len(data["edges"]) == 1
    assert data["edges"][0]["node"]["id"] == global_id


def test_investments_staff_query(staff_api_client, investment, published_investment):
    variables = {"first": 10}
    response = staff_api_client.post_graphql(QUERY_INVESTMENTS, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["investments"]

    assert len(data["edges"]) == 2


def test_investments_staff_query_with_filter(
    staff_api_client, investment, published_investment
):
    variables = {"first": 10, "filter": {"isPublished": False}}
    response = staff_api_client.post_graphql(QUERY_INVESTMENTS, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["investments"]
    global_id = graphene.Node.to_global_id("Investment", investment.pk)

    assert len(data["edges"]) == 1
    assert data["edges"][0]["node"]["id"] == global_id


def test_investments_by_channel(api_client, published_investment, channel_city_1):
    variables = {"first": 10, "channel": channel_city_1.slug}
    response = api_client.post_graphql(QUERY_INVESTMENTS, variables=variables)
    content = get_graphql_content(response)
    data = content["data"]["investments"]
    global_id = graphene.Node.to_global_id("Investment", published_investment.pk)

    assert len(data["edges"]) == 1
    assert data["edges"][0]["node"]["id"] == global_id
