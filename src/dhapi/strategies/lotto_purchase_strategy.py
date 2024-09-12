from typing import List

from dhapi.constants import Lotto645Mode
from dhapi.interfaces.lotto_purchase_strategy import LottoPurchaseStrategy


class AutoPurchaseStrategy(LottoPurchaseStrategy):
	def generate_numbers(self) -> List[int]:
		return []  # 자동 생성은 서버에서 처리되므로 빈 리스트 반환


class SemiAutoPurchaseStrategy(LottoPurchaseStrategy):
	def __init__(self, fixed_numbers: List[int]):
		self.fixed_numbers = fixed_numbers

	def generate_numbers(self) -> List[int]:
		return self.fixed_numbers


class ManualPurchaseStrategy(LottoPurchaseStrategy):
	def __init__(self, numbers: List[int]):
		self.numbers = numbers

	def generate_numbers(self) -> List[int]:
		return self.numbers


class Lotto645Ticket:
	def __init__(self, strategy: LottoPurchaseStrategy):
		self.strategy = strategy
		self.numbers = self.strategy.generate_numbers()
		self.mode = self._determine_mode()

	def _determine_mode(self) -> Lotto645Mode:
		if isinstance(self.strategy, AutoPurchaseStrategy):
			return Lotto645Mode.AUTO
		elif isinstance(self.strategy, SemiAutoPurchaseStrategy):
			return Lotto645Mode.SEMIAUTO
		elif isinstance(self.strategy, ManualPurchaseStrategy):
			return Lotto645Mode.MANUAL
		else:
			raise ValueError("Invalid purchase strategy")

	@property
	def mode_kor(self) -> str:
		mode_mapping = {
			Lotto645Mode.AUTO: "자동",
			Lotto645Mode.SEMIAUTO: "반자동",
			Lotto645Mode.MANUAL: "수동",
		}
		return mode_mapping.get(self.mode, "알 수 없음")

	@classmethod
	def create_auto_tickets(cls, count: int) -> List['Lotto645Ticket']:
		return [cls(AutoPurchaseStrategy()) for _ in range(count)]

	@classmethod
	def create_tickets(cls, numbers_list: List[str]) -> List['Lotto645Ticket']:
		tickets = []
		for numbers in numbers_list:
			if not numbers:
				tickets.append(cls(AutoPurchaseStrategy()))
			else:
				number_list = [int(n) for n in numbers.split(',')]
				if len(number_list) == 6:
					tickets.append(cls(ManualPurchaseStrategy(number_list)))
				else:
					tickets.append(cls(SemiAutoPurchaseStrategy(number_list)))
		return tickets
