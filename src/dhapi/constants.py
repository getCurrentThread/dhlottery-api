from enum import Enum


# LotteryClient 관련 상수
class LotteryEndpoints:
	BASE_URL = "https://dhlottery.co.kr"
	DEFAULT_SESSION = "/gameResult.do?method=byWin&wiselog=H_C_1_1"
	SYSTEM_UNDER_CHECK = "/index_check.html"
	MAIN = "/common.do?method=main"
	LOGIN = "/userSsl.do?method=login"
	BUY_LOTTO645 = "https://ol.dhlottery.co.kr/olotto/game/execBuy.do"
	READY_SOCKET = "https://ol.dhlottery.co.kr/olotto/game/egovUserReadySocket.json"
	CASH_BALANCE = "/userSsl.do?method=myPage"
	ASSIGN_VIRTUAL_ACCOUNT_1 = "/nicePay.do?method=nicePayInit"
	ASSIGN_VIRTUAL_ACCOUNT_2 = "/nicePay.do?method=nicePayProcess"


# HTTP 헤더 관련 상수
DEFAULT_HEADERS = {
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
	"Connection": "keep-alive",
	"Cache-Control": "max-age=0",
	"sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
	"sec-ch-ua-mobile": "?0",
	"Upgrade-Insecure-Requests": "1",
	"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"Sec-Fetch-Site": "same-site",
	"Sec-Fetch-Mode": "navigate",
	"Sec-Fetch-User": "?1",
	"Sec-Fetch-Dest": "document",
	"Accept-Language": "ko,en-US;q=0.9,en;q=0.8,ko-KR;q=0.7",
	"X-Requested-With": "XMLHttpRequest",
}


# Lotto645 관련 상수
class Lotto645Constants:
	MIN_NUMBER = 1
	MAX_NUMBER = 45
	NUMBERS_PER_TICKET = 6
	MAX_TICKETS_PER_PURCHASE = 5
	TICKET_PRICE = 1000  # 원


class Lotto645Mode(Enum):
	AUTO = "auto"
	SEMIAUTO = "semiauto"
	MANUAL = "manual"


# Deposit 관련 상수
VALID_DEPOSIT_AMOUNTS = [5000, 10000, 20000, 30000, 50000, 100000, 200000, 300000, 500000, 700000, 1000000]

# 기타 상수
VBANK_BANK_CODE = "089"  # 가상계좌 채번가능 케이뱅크 코드
GOODS_NAME = "복권예치금"
PAY_METHOD = "VBANKFVB01"
