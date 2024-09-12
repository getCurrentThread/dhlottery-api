import logging
from dhapi.constants import VALID_DEPOSIT_AMOUNTS

logger = logging.getLogger(__name__)


class Deposit:
	def __init__(self, amount: int):
		self.amount = self._validate_amount(amount)

	@staticmethod
	def _validate_amount(amount: int) -> int:
		try:
			amount = int(amount)
		except ValueError:
			raise ValueError(f"숫자를 입력하세요 (입력된 값: {amount}).")

		if amount not in VALID_DEPOSIT_AMOUNTS:
			raise ValueError(f"입금 가능한 금액은 {', '.join(map(str, VALID_DEPOSIT_AMOUNTS))}원입니다 (입력된 값: {amount}).")

		return amount
