# arbi1

.key.ini파일 생성

api키 생성하여 (바이낸스, 업비트 내 정보->OpenAPI) 하기 키 값 넣어야 동작함

{
    "upbit":{
        "accKey":"",
        "secKey":""
    },
    "binance":{
        "apiKey":"",
        "secKey":""
    }
}

김프 가격 모니터링
python kimp-monitor.py

김프 차트 생성
- arbiRanges에 기간, OUT_TH(UB->BN), IN_TH(BN->UB)지정
python arb-comp.py

내 지갑 밸런스 확인
python balance.py

아비트라지 인, 아웃 테스트
python test.py

아비트라지 실행
- IN_TH, OUT_TH 파라메터값 편집
- maxUSD값이 한번에 옮길 비용 크기
- STATUS_CHANGE = True면 하나의 바이너리로 왔다 갔다, False면 
 status='UB' 바이너리 하나, status='BN'바이너리 하나 생성해서 둘다 독립적으로 돌게 함
python main.py