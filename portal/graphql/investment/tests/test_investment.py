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
            items{
                id
                name
                value
            }
        }
    }
"""

QUERY_INVESTMENTS = """
    query Investments($first: Int, $filter: InvestmentFilterInput){
        investments(first: $first, filter: $filter){
            edges{
                node{
                    id
                    month
                    year
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


CREATE_INVESTMENT_MUTATION = """
    mutation InvestmentCreate($input: InvestmentInput!){
        investmentCreate(input: $input){
            investment{
                id
                month
                year
                items{
                    id
                    name
                    value
                }
            }
            errors{
                message
                field
                code
            }
        }
    }
"""


def test_investment_create_mutation(staff_api_client, permission_manage_investments):
    input = {"month": 6, "year": 2022}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_INVESTMENT_MUTATION,
        permissions=[permission_manage_investments],
        variables=variables,
    )
    content = get_graphql_content(response)
    data = content["data"]["investmentCreate"]
    assert data["errors"] == []
    assert data["investment"]["month"] == input["month"]
    assert data["investment"]["year"] == input["year"]


def test_investment_create_mutation_missing_params(
    staff_api_client, permission_manage_investments
):
    input = {
        "month": 6,
    }
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_INVESTMENT_MUTATION,
        permissions=[permission_manage_investments],
        variables=variables,
    )
    content = get_graphql_content(response)
    data = content["data"]["investmentCreate"]

    assert data["investment"] is None
    assert data["errors"] is not None
    assert data["errors"][0]["field"] == "year"


def test_investment_create_mutation_duplicated(
    staff_api_client, permission_manage_investments
):
    input = {"month": 6, "year": 2022}
    variables = {"input": input}
    response = staff_api_client.post_graphql(
        CREATE_INVESTMENT_MUTATION,
        permissions=[permission_manage_investments],
        variables=variables,
    )
    response = staff_api_client.post_graphql(
        CREATE_INVESTMENT_MUTATION,
        permissions=[permission_manage_investments],
        variables=variables,
    )
    content = get_graphql_content(response)

    data = content["data"]["investmentCreate"]
    assert data["investment"] is None
    assert data["errors"] is not None
    assert data["errors"][0]["code"] == "unique_together"


UPDATE_INVESTMENT_MUTATION = """
    mutation InvestmentUpdate($id: ID, $input: InvestmentUpdateInput!){
        investmentUpdate(id: $id, input: $input){
            investment{
                id
                month
                year
                isPublished
                items{
                    id
                    name
                    value
                }
            }
            errors{
                message
                field
                code
            }
        }
    }
"""


def test_investment_update_mutation(
    staff_api_client, permission_manage_investments, investment
):
    investment_id = graphene.Node.to_global_id("Investment", investment.pk)
    input = {"month": 12, "isPublished": True}
    variables = {"id": investment_id, "input": input}
    response = staff_api_client.post_graphql(
        UPDATE_INVESTMENT_MUTATION,
        permissions=[permission_manage_investments],
        variables=variables,
    )
    content = get_graphql_content(response)
    data = content["data"]["investmentUpdate"]
    assert data["errors"] == []
    assert data["investment"]["id"] == investment_id
    assert data["investment"]["month"] == input["month"]
    assert data["investment"]["isPublished"] == input["isPublished"]


def test_investment_update_mutation_invalid_parameter(
    staff_api_client, permission_manage_investments, investment, published_investment
):
    investment_id = graphene.Node.to_global_id("Investment", investment.pk)
    input = {"month": 2, "isPublished": True}
    variables = {"id": investment_id, "input": input}
    response = staff_api_client.post_graphql(
        UPDATE_INVESTMENT_MUTATION,
        permissions=[permission_manage_investments],
        variables=variables,
    )
    content = get_graphql_content(response)
    data = content["data"]["investmentUpdate"]

    assert data["investment"] is None
    assert data["errors"] is not None
    assert data["errors"][0]["code"] == "unique_together"


INVESTMENT_DELETE_MUTATION = """
    mutation($id: ID!) {
        investmentDelete(id: $id) {
            investment {
                id
            }
            errors {
                field
                message
            }
        }
    }
"""


def test_investment_delete_mutation(
    staff_api_client,
    permission_manage_investments,
    investment,
):
    investment_id = graphene.Node.to_global_id("Investment", investment.id)
    variables = {"id": investment_id}
    response = staff_api_client.post_graphql(
        INVESTMENT_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_investments],
    )
    content = get_graphql_content(response)
    data = content["data"]["investmentDelete"]

    assert data["errors"] == []
    assert data["investment"]["id"] == investment_id


def test_investment_delete_mutation_with_invalid_id(
    staff_api_client,
    permission_manage_investments,
    investment,
):
    variables = {"id": "'"}
    response = staff_api_client.post_graphql(
        INVESTMENT_DELETE_MUTATION,
        variables=variables,
        permissions=[permission_manage_investments],
    )
    content = get_graphql_content(response)
    data = content["data"]["investmentDelete"]

    assert data["investment"] is None
    assert data["errors"] is not None
    assert data["errors"][0]["field"] == "id"


ITEM_BULK_CREATE_MUTATION = """
    mutation($investmentId: ID!, $items: [ItemBulkInput]!) {
        itemBulkCreate(investmentId: $investmentId, items: $items) {
            items{
                id
                name
                investment{
                    id
                }
            }
            errors{
                index
                message
                field
                code
            }
        }
    }
"""


def test_items_bulk_create(
    staff_api_client,
    permission_manage_items,
    investment,
):
    investment_id = graphene.Node.to_global_id("Investment", investment.id)
    variables = {
        "investmentId": investment_id,
        "items": [{"name": "Item 1", "value": 10}, {"name": "Item 2", "value": 20}],
    }
    response = staff_api_client.post_graphql(
        ITEM_BULK_CREATE_MUTATION,
        variables=variables,
        permissions=[permission_manage_items],
    )
    content = get_graphql_content(response)
    data = content["data"]["itemBulkCreate"]

    assert data["errors"] == []
    assert len(data["items"]) == 2
    assert data["items"][0]["investment"]["id"] == investment_id
