from typing import Dict, List
from rich.console import Console
from rich.table import Table

from dhapi.interfaces.lotto_purchase_observer import LottoPurchaseObserver



class LotteryStdoutPrinter(LottoPurchaseObserver):
    def __init__(self):
        self.console = Console()

    def update(self, slots: List[Dict[str, str]]):
        self.print_result_of_buy_lotto645(slots)

    def print_result_of_assign_virtual_account(self, 전용가상계좌: str, 결제신청금액: str) -> None:
        self.console.print("✅ 가상계좌를 할당했습니다.")
        self.console.print("❗️입금 전 계좌주 이름을 꼭 확인하세요.")
        table = Table("전용가상계좌", "결제신청금액")
        table.add_row(전용가상계좌, 결제신청금액)
        self.console.print(table)

    def print_result_of_show_balance(self, 총예치금: int, 구매가능금액: int, 예약구매금액: int,
                                     출금신청중금액: int, 구매불가능금액: int, 이번달누적구매금액: int) -> None:
        self.console.print("✅ 예치금 현황을 조회했습니다.")
        table = Table("총예치금", "구매가능금액", "예약구매금액", "출금신청중금액", "구매불가능금액", "이번달누적구매금액")
        table.add_row(
            self._num_to_money_str(총예치금),
            self._num_to_money_str(구매가능금액),
            self._num_to_money_str(예약구매금액),
            self._num_to_money_str(출금신청중금액),
            self._num_to_money_str(구매불가능금액),
            self._num_to_money_str(이번달누적구매금액),
        )
        self.console.print(table)
        self.console.print("[dim](구매불가능금액 = 예약구매금액 + 출금신청중금액)[/dim]")

    def _num_to_money_str(self, num: int) -> str:
        return f"{num:,} 원"

    def print_result_of_buy_lotto645(self, slots: List[Dict[str, str]]) -> None:
        self.console.print("✅ 로또6/45 복권을 구매했습니다.")
        table = Table("슬롯", "Mode", "번호1", "번호2", "번호3", "번호4", "번호5", "번호6")
        for slot in slots:
            table.add_row(slot["slot"], slot["mode"], *slot["numbers"])
        self.console.print(table)