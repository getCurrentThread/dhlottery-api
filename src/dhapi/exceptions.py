class DhapiError(Exception):
	"""dhapi의 기본 예외 클래스"""


class LotteryClientError(DhapiError):
	"""LotteryClient에서 발생하는 오류에 대한 예외"""


class AuthenticationError(LotteryClientError):
	"""인증 실패 시 발생하는 예외"""


class NetworkError(LotteryClientError):
	"""네트워크 관련 오류에 대한 예외"""


class PurchaseError(LotteryClientError):
	"""복권 구매 과정에서 발생하는 오류에 대한 예외"""


class BalanceError(LotteryClientError):
	"""잔액 관련 작업에서 발생하는 오류에 대한 예외"""


class TicketCreationError(DhapiError):
	"""티켓 생성 과정에서 발생하는 오류에 대한 예외"""


class InvalidNumberError(TicketCreationError):
	"""유효하지 않은 복권 번호에 대한 예외"""
