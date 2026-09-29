class ToolError(Exception):
    """Base error for investigation tool execution."""


class PaymentNotFoundError(ToolError):
    def __init__(self, payment_id: str) -> None:
        self.payment_id = payment_id
        super().__init__(f"Payment {payment_id} was not found.")
