from abc import ABC, abstractmethod
from typing import List


class LottoPurchaseStrategy(ABC):
	@abstractmethod
	def generate_numbers(self) -> List[int]:
		pass
