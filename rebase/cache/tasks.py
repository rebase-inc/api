
from rebase.models import (
    Auction,
)
from rebase.views import auction as auction_views


def warmup(role):
    from rebase.common.rest import get_collection
    print('Warming up for {}'.format(role))
    response = get_collection(Auction, auction_views.serializer, role.user)
    print('Computed:')
    print(response)

