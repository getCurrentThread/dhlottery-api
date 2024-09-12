from dhapi.domain.lotto645_ticket import Lotto645Ticket
from dhapi.strategies.lotto_purchase_strategy import *
from dhapi import constants


class Lotto645TicketFactory:
	@staticmethod
	def create_ticket(numbers: str = None) -> Lotto645Ticket:
		if not numbers:
			return Lotto645Ticket(AutoPurchaseStrategy())

		number_list = [int(n) for n in numbers.split(',')]

		if len(number_list) == constants.NUMBERS_PER_TICKET:
			return Lotto645Ticket(ManualPurchaseStrategy(number_list))
		else:
			return Lotto645Ticket(SemiAutoPurchaseStrategy(number_list))

	@staticmethod
	def create_auto_tickets(count: int) -> List[Lotto645Ticket]:
		return [Lotto645TicketFactory.create_ticket() for _ in range(count)]

	@staticmethod
	def create_tickets(numbers_list: List[str]) -> List[Lotto645Ticket]:
		return [Lotto645TicketFactory.create_ticket(numbers) for numbers in numbers_list]
