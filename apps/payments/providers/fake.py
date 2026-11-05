class FakeProvider:
    auto_settle = True

    def reference_for(self, payout):
        return f"FAKE-{payout.pk}"

    def send(self, payout):
        pass
