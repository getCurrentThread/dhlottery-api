import logging
from typing import List, Dict, Any
import datetime
import json
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import pytz

from dhapi.domain.lotto645_ticket import Lotto645Ticket
from dhapi.domain.deposit import Deposit
from dhapi.domain.user import User
from dhapi.exceptions import *
from dhapi.constants import LotteryEndpoints, DEFAULT_HEADERS, Lotto645Constants, VBANK_BANK_CODE, GOODS_NAME, PAY_METHOD

logger = logging.getLogger(__name__)


class LotteryClient:

	def __init__(self, user_profile: User):
		if not hasattr(self, '_initialized'):
			self._user_id = user_profile.username
			self._user_pw = user_profile.password
			self._headers = DEFAULT_HEADERS.copy()
			self._headers["Origin"] = LotteryEndpoints.BASE_URL
			self._headers["Referer"] = LotteryEndpoints.BASE_URL
			self._session = requests.Session()
			self._observers: List[LottoPurchaseObserver] = []
			self._set_default_session()
			self._login()

	def _set_default_session(self) -> None:
		try:
			resp = self._session.get(LotteryEndpoints.BASE_URL + LotteryEndpoints.DEFAULT_SESSION, timeout=10)
			resp.raise_for_status()

			if resp.url == LotteryEndpoints.BASE_URL + LotteryEndpoints.SYSTEM_UNDER_CHECK:
				raise LotteryClientError("동행복권 사이트가 현재 시스템 점검중입니다.")

			jsessionid = resp.cookies.get("JSESSIONID")
			if not jsessionid:
				raise LotteryClientError("JSESSIONID 쿠키가 정상적으로 세팅되지 않았습니다.")

			self._headers["Cookie"] = f"JSESSIONID={jsessionid}"
		except RequestException as e:
			raise NetworkError(f"네트워크 오류가 발생했습니다: {str(e)}") from e

	def _login(self) -> None:
		try:
			resp = self._session.post(
				LotteryEndpoints.BASE_URL + LotteryEndpoints.LOGIN,
				headers=self._headers,
				data={
					"returnUrl": LotteryEndpoints.BASE_URL + LotteryEndpoints.MAIN,
					"userId": self._user_id,
					"password": self._user_pw,
					"checkSave": "off",
					"newsEventYn": "",
				},
				timeout=10
			)
			resp.raise_for_status()

			soup = BeautifulSoup(resp.text, "html5lib")
			if soup.find("a", {"class": "btn_common"}):
				raise AuthenticationError("로그인에 실패했습니다. 아이디 또는 비밀번호를 확인해주세요.")
		except RequestException as e:
			raise NetworkError(f"로그인 중 네트워크 오류가 발생했습니다: {str(e)}") from e

	def _get_round(self) -> int:
		try:
			resp = self._session.get(LotteryEndpoints.BASE_URL + LotteryEndpoints.MAIN, timeout=10)
			resp.raise_for_status()
			soup = BeautifulSoup(resp.text, "html5lib")

			elem = soup.find("strong", {"id": "lottoDrwNo"})
			if not elem:
				raise LotteryClientError("현재 회차 정보를 가져올 수 없습니다.")

			return int(elem.text) + 1
		except RequestException as e:
			raise NetworkError(f"회차 정보를 가져오는 중 네트워크 오류가 발생했습니다: {str(e)}") from e
		except ValueError as e:
			raise LotteryClientError(f"회차 정보 파싱 중 오류가 발생했습니다: {str(e)}") from e

	def buy_lotto645(self, tickets: List[Lotto645Ticket]) -> None:
		if len(tickets) > Lotto645Constants.MAX_TICKETS_PER_PURCHASE:
			raise PurchaseError(f"한 번에 최대 {Lotto645Constants.MAX_TICKETS_PER_PURCHASE}장까지만 구매할 수 있습니다.")

		try:
			resp = self._session.post(LotteryEndpoints.READY_SOCKET, headers=self._headers, timeout=10)
			resp.raise_for_status()
			direct = resp.json()["ready_ip"]

			data = {
				"round": str(self._get_round()),
				"direct": direct,
				"nBuyAmount": str(Lotto645Constants.TICKET_PRICE * len(tickets)),
				"param": self._make_buy_lotto645_param(tickets),
				"gameCnt": len(tickets),
			}

			resp = self._session.post(
				LotteryEndpoints.BUY_LOTTO645,
				headers=self._headers,
				data=data,
				timeout=10
			)
			resp.raise_for_status()

			response = resp.json()
			if not self._is_purchase_success(response):
				raise PurchaseError(f"로또6/45 구매에 실패했습니다. (사유: {response['result']['resultMsg']})")

			slots = self._format_lotto_numbers(response["result"]["arrGameChoiceNum"])
			self.notify_observers(slots)
		except RequestException as e:
			raise NetworkError(f"로또 구매 중 네트워크 오류가 발생했습니다: {str(e)}") from e
		except (KeyError, ValueError) as e:
			raise PurchaseError(f"로또 구매 응답을 처리하는 중 오류가 발생했습니다: {str(e)}") from e

	def _is_purchase_success(self, response: Dict[str, Any]) -> bool:
		return response["result"]["resultCode"] == "100"

	def _make_buy_lotto645_param(self, tickets: List[Lotto645Ticket]) -> str:
		params = []
		for i, t in enumerate(tickets):
			if t.mode == Lotto645Constants.AUTO:
				gen_type = "0"
			elif t.mode == Lotto645Constants.MANUAL:
				gen_type = "1"
			elif t.mode == Lotto645Constants.SEMIAUTO:
				gen_type = "2"
			else:
				raise PurchaseError(f"올바르지 않은 모드입니다. (mode: {t.mode})")
			arr_game_choice_num = None if t.mode == Lotto645Constants.AUTO else ",".join(map(str, t.numbers))
			alpabet = "ABCDE"[i]  # XXX: 오타 아님
			slot = {
				"genType": gen_type,
				"arrGameChoiceNum": arr_game_choice_num,
				"alpabet": alpabet,
			}
			params.append(slot)
		return json.dumps(params)

	def _format_lotto_numbers(self, lines: List[str]) -> List[Dict[str, Any]]:
		mode_dict = {
			"1": "수동",
			"2": "반자동",
			"3": "자동",
		}

		slots = []
		for line in lines:
			slot = {
				"mode": mode_dict[line[-1]],
				"slot": line[0],
				"numbers": line[2:-1].split("|"),
			}
			slots.append(slot)
		return slots

	def show_balance(self) -> None:
		try:
			resp = self._session.get(LotteryEndpoints.BASE_URL + LotteryEndpoints.CASH_BALANCE, headers=self._headers, timeout=10)
			resp.raise_for_status()

			soup = BeautifulSoup(resp.text, "html5lib")

			has_bank_account = bool(soup.select_one(".tbl_total_account_number_top tbody tr td").contents)
			elem = soup.select("div.box.money")[0]

			if has_bank_account:
				# 간편충전 계좌번호가 있는 경우
				총예치금 = self._parse_digit(elem.select("p.total_new > strong")[0].contents[0])
				구매가능금액 = self._parse_digit(elem.select("td.ta_right")[3].contents[0])
				예약구매금액 = self._parse_digit(elem.select("td.ta_right")[4].contents[0])
				출금신청중금액 = self._parse_digit(elem.select("td.ta_right")[5].contents[0])
				구매불가능금액 = self._parse_digit(elem.select("td.ta_right")[6].contents[0])
				이번달누적구매금액 = self._parse_digit(elem.select("td.ta_right")[7].contents[0])
			else:
				# 간편충전 계좌번호가 없는 경우
				총예치금 = self._parse_digit(elem.select("p.total_new > strong")[0].contents[0])
				구매가능금액 = self._parse_digit(elem.select("td.ta_right")[1].contents[0])
				예약구매금액 = self._parse_digit(elem.select("td.ta_right")[2].contents[0])
				출금신청중금액 = self._parse_digit(elem.select("td.ta_right")[3].contents[0])
				구매불가능금액 = self._parse_digit(elem.select("td.ta_right")[4].contents[0])
				이번달누적구매금액 = self._parse_digit(elem.select("td.ta_right")[5].contents[0])

			return 총예치금, 구매가능금액, 예약구매금액, 출금신청중금액, 구매불가능금액, 이번달누적구매금액

		except RequestException as e:
			raise NetworkError(f"잔액 조회 중 네트워크 오류가 발생했습니다: {str(e)}") from e
		except (AttributeError, IndexError) as e:
			raise BalanceError(f"잔액 정보를 파싱하는 중 오류가 발생했습니다: {str(e)}") from e

	def _parse_digit(self, text: str) -> int:
		return int("".join(filter(str.isdigit, text)))

	def assign_virtual_account(self, deposit: Deposit) -> None:
		try:
			resp = self._session.post(
				LotteryEndpoints.BASE_URL + LotteryEndpoints.ASSIGN_VIRTUAL_ACCOUNT_1,
				headers=self._headers,
				data={
					"PayMethod": PAY_METHOD,
					"VbankBankCode": VBANK_BANK_CODE,
					"price": str(deposit.amount),
					"goodsName": GOODS_NAME,
					"vExp": self._get_tomorrow(),
				},
				timeout=10
			)
			resp.raise_for_status()

			data = resp.json()
			logger.debug(f"data: {data}")

			body = {
				"PayMethod": data["PayMethod"],
				"GoodsName": data["GoodsName"],
				"GoodsCnt": data["GoodsCnt"],
				"BuyerTel": data["BuyerTel"],
				"Moid": data["Moid"],
				"MID": data["MID"],
				"UserIP": data["UserIP"],
				"MallIP": data["MallIP"],
				"MallUserID": data["MallUserID"],
				"VbankExpDate": data["VbankExpDate"],
				"BuyerEmail": data["BuyerEmail"],
				"SocketYN": data["SocketYN"],
				"GoodsCl": data["GoodsCl"],
				"EncodeParameters": data["EncodeParameters"],
				"EdiDate": data["EdiDate"],
				"EncryptData": data["EncryptData"],
				"Amt": data["amt"],
				"BuyerName": data["BuyerName"],
				"VbankBankCode": data["VbankBankCode"],
				"VbankNum": data["FxVrAccountNo"],
				"FxVrAccountNo": data["FxVrAccountNo"],
				"VBankAccountName": data["BuyerName"],
				"svcInfoPgMsgYn": "N",
				"OptionList": "no_receipt",
				"TransType": "0",  # 일반(0), 에스크로(1)
				"TrKey": None,
			}

			resp = self._session.post(LotteryEndpoints.BASE_URL + LotteryEndpoints.ASSIGN_VIRTUAL_ACCOUNT_2, headers=self._headers, data=body,
			                          timeout=10)
			resp.raise_for_status()

			soup = BeautifulSoup(resp.text, "html5lib")

			elem = soup.select("#contents")

			전용가상계좌 = elem[0].select("span")[0].contents[0]
			결제신청금액 = elem[0].select(".color_key1")[0].contents[0]

			return 전용가상계좌, 결제신청금액
		except RequestException as e:
			raise NetworkError(f"가상계좌 할당 중 네트워크 오류가 발생했습니다: {str(e)}") from e
		except (KeyError, ValueError, IndexError) as e:
			raise BalanceError(f"가상계좌 정보를 처리하는 중 오류가 발생했습니다: {str(e)}") from e

	def _get_tomorrow(self) -> str:
		korea_tz = pytz.timezone("Asia/Seoul")
		now = datetime.datetime.now(korea_tz)
		tomorrow = now + datetime.timedelta(days=1)
		return tomorrow.strftime("%Y%m%d")

	def add_observer(self, observer: LottoPurchaseObserver):
		if observer not in self._observers:
			self._observers.append(observer)

	def remove_observer(self, observer: LottoPurchaseObserver):
		if observer in self._observers:
			self._observers.remove(observer)

	def notify_observers(self, slots: List[Dict[str, str]]):
		for observer in self._observers:
			observer.update(slots)
