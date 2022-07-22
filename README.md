# Code Review 관련
1. python을 거의 처음쓰면서 만든거라 package등 및 add-hoc한 부분이 많습니다.
2. kimp를 통한 차익 매매프로그램인데, 일단 돈버는게 중요해서 class대신 c style로 name space만 주면서 사용했습니다.
3. 전체적인 구조는 main.py에서 loop을 돌면서 kimp를 모니터링하고 (calc_kimp) 조건 만족시 arbi/arbi_wrapper.py의 arbi_in_bn_to_ub(바낸에서 업빗으로 입국), arbi_out_ub_to_bn(업빗에서 바낸으로 출국)을 수행합니다.
4. arbi_wrapper.py에서 arbi_in.py(입국관련) 및 arbi_out.py(출국관련)으로 분리되있습니다.
5. arbi_in|out.py에서 매매 및 거래소간 이동 로직을 수행하고, exchange/bn.py(바이낸스), ub.py(업비트) 관련 거래소 api를 wrapping한 코드를 호출합니다.
6. exchange/bn.py와 ub.py는 혼동이 없도록 최대한 동일한 function prototype으로 만들어져있습니다.
7. spot(현물) 및 futures(선물)도 namespace만 다르고 function prototype은 최대한 동일하게 만들었습니다.
8. 일부 future 매매로직에 시간 딜레이를 없애기 위해 threading이 적용되었습니다 (테스트로 sync로 만들다가 async로 만들기에 시간이 없어 일부 필요구간만 수정)
9. 기타 다른 .py들은 테스트용 데이터 다운로드, 김프 그래프 그리기 등 별도 파일이나 개인프로젝트이고 일단 돌리는게 목적이라 정리가 안된체로 혼재되있는 점 양해 부탁 드립니다.
10. 현재 해당 프로젝트는 stable하게 돈을 벌기는 어렵다는 판단이 들어 추가 개발은 하고 있지 않습니다.
 
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
