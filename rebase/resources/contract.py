from flask import current_app

from rebase.common.keys import make_collection_url, make_resource_url
from rebase.models.contract import Contract
from rebase.resources import RestfulResource, RestfulCollection
import rebase.views.contract as contract_views


ContractResource = RestfulResource(
    Contract,
    contract_views.serializer,
    contract_views.deserializer,
    contract_views.update_deserializer,
)


ContractCollection = RestfulCollection(
    Contract,
    contract_views.serializer,
    contract_views.deserializer,
    cache=True
)


get_all_contracts = ContractCollection.get_all


def add_contract_resource(api):
    api.add_resource(ContractCollection, make_collection_url(Contract), endpoint = Contract.__pluralname__)
    api.add_resource(ContractResource, make_resource_url(Contract), endpoint = Contract.__pluralname__ + '_resource')


