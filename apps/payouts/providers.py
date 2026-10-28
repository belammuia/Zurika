class ProviderRejected(Exception):
    """The provider definitely did not take the payment."""


class FakeProvider:
    auto_settle = True  

    def send(self, payout):
        return f"FAKE-{payout.pk}"


def get_provider(method):
    
    return FakeProvider()