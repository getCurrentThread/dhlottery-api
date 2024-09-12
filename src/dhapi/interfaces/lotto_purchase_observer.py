from abc import ABC, abstractmethod
from typing import List, Dict


class LottoPurchaseObserver(ABC):
	@abstractmethod
	def update(self, slots: List[Dict[str, str]]):
		pass
