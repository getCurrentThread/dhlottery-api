from typing import List
from dhapi.exceptions import InvalidNumberError
from dhapi.constants import Lotto645Constants, Lotto645Mode
from dhapi.strategies.lotto_purchase_strategy import AutoPurchaseStrategy, SemiAutoPurchaseStrategy, ManualPurchaseStrategy
from dhapi.interfaces.lotto_purchase_strategy import LottoPurchaseStrategy


class Lotto645Ticket:
	def __init__(self, strategy: LottoPurchaseStrategy):
		self.strategy = strategy
		self.numbers = self._validate_numbers(self.strategy.generate_numbers())
		self.mode = self._determine_mode()

	def _validate_numbers(self, numbers: List[int]) -> List[int]:
		if not all(isinstance(n, int) for n in numbers):
			raise InvalidNumberError("모든 번호는 정수여야 합니다.")

		if len(numbers) > Lotto645Constants.NUMBERS_PER_TICKET:
			raise InvalidNumberError(f"번호는 최대 {Lotto645Constants.NUMBERS_PER_TICKET}개까지만 선택할 수 있습니다. (입력된 개수: {len(numbers)})")

		if len(set(numbers)) != len(numbers):
			raise InvalidNumberError("중복된 번호가 있습니다.")

		if any(n < Lotto645Constants.MIN_NUMBER or n > Lotto645Constants.MAX_NUMBER for n in numbers):
			raise InvalidNumberError(f"모든 번호는 {Lotto645Constants.MIN_NUMBER}부터 {Lotto645Constants.MAX_NUMBER} 사이의 숫자여야 합니다.")

		return sorted(numbers)

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
		if count < 1 or count > Lotto645Constants.MAX_TICKETS_PER_PURCHASE:
			raise ValueError(f"자동 티켓은 1에서 {Lotto645Constants.MAX_TICKETS_PER_PURCHASE}장 사이로만 생성할 수 있습니다. (요청된 개수: {count})")
		return [cls(AutoPurchaseStrategy()) for _ in range(count)]

	@classmethod
	def create_tickets(cls, numbers_list: List[str]) -> List['Lotto645Ticket']:
		if len(numbers_list) > Lotto645Constants.MAX_TICKETS_PER_PURCHASE:
			raise ValueError(f"한 번에 최대 {Lotto645Constants.MAX_TICKETS_PER_PURCHASE}장의 티켓만 생성할 수 있습니다. (요청된 개수: {len(numbers_list)})")

		tickets = []
		for numbers in numbers_list:
			if not numbers:
				tickets.append(cls(AutoPurchaseStrategy()))
			else:
				number_list = [int(n.strip()) for n in numbers.split(',')]
				if len(number_list) == Lotto645Constants.NUMBERS_PER_TICKET:
					tickets.append(cls(ManualPurchaseStrategy(number_list)))
				elif 1 <= len(number_list) < Lotto645Constants.NUMBERS_PER_TICKET:
					tickets.append(cls(SemiAutoPurchaseStrategy(number_list)))
				else:
					raise InvalidNumberError(f"유효하지 않은 번호 개수입니다: {len(number_list)}")
		return tickets

	def __str__(self) -> str:
		return f"Lotto645Ticket(mode={self.mode_kor}, numbers={self.numbers})"

	def __repr__(self) -> str:
		return self.__str__()
