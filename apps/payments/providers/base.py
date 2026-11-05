class ProviderRejected(Exception):
    """The provider definitely did not take the payment."""


def normalize_phone(raw):
    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    if len(digits) == 10 and digits.startswith("0"):
        digits = "254" + digits[1:]
    if not (len(digits) == 12 and digits.startswith("254")):
        raise ProviderRejected("Invalid phone number")
    return digits
