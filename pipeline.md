"Altcoin Discovery Project" 보고서는 `/home/ivjiyeonb/projects/altcoin_discovery/cron_job_script.py` 스크립트를 통해 다음 순서로 생성됩니다.

1.  **데이터 획득 및 분석 (Data Acquisition and Analysis)**
    *   스크립트는 먼저 `get_binance_data_ccxt.py`와 `analyze_data.py` 두 개의 서브스크립트를 순차적으로 실행합니다.
    *   `get_binance_data_ccxt.py`는 바이낸스(Binance)와 같은 거래소에서 OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터를 포함한 최신 알트코인 시장 데이터를 수집합니다.
    *   수집된 데이터는 `analyze_data.py`로 파이프(pipe)되어 전달됩니다.
    *   `analyze_data.py`는 이 데이터를 분석하여 잠재력 있는 새로운 알트코인 추천 목록과 각 코인의 현재 가격, 예상 목표가 등을 산출합니다. 분석 결과는 JSON 형식으로 반환됩니다.

2.  **기존 추천 내역 로드 (Load Existing Recommendation History)**
    *   스크립트는 `recommendation_history.json` 파일을 읽어들여 이전에 추천했던 알트코인들의 기록을 불러옵니다.
    *   만약 파일이 없거나 비어 있다면, 빈 추천 내역으로 시작합니다.

3.  **새로운 추천 처리 (Process New Recommendations)**
    *   1단계에서 `analyze_data.py`로부터 얻은 새로운 알트코인 추천 목록에 현재 날짜(`recommendation_date`)를 추가합니다.
    *   새로운 추천들을 기존 추천 내역(`recommendation_history`)에 추가합니다.

4.  **과거 추천 검토 (Review Past Recommendations)**
    *   업데이트된 추천 내역(`recommendation_history`)을 반복하며 각 과거 추천 코인의 성능을 검토합니다.
    *   **목표 달성 확인**: 현재 코인 가격이 추천 당시 가격보다 30% 이상 상승했으면 "목표 달성(Hit)"으로 분류합니다.
    *   **포기된 코인 확인**: 목표를 달성하지 못했고 추천일로부터 2주(14일) 이상 경과한 코인은 "포기된 코인(Abandoned)"으로 분류합니다.
    *   목표를 달성했거나 포기된 코인은 `recommendation_history`에서 제외됩니다.
    *   현재 가격을 알 수 없는 코인은 검토 대상에서 제외하고 다음 검토를 위해 `recommendation_history`에 유지합니다.

5.  **리포트 생성 (Generate Discord Report)**
    *   위에서 처리된 신규 추천 코인과 과거 추천 코인 검토(목표 달성, 포기된 코인) 결과를 바탕으로 디스코드에 게시될 보고서 내용을 마크다운 형식으로 작성합니다.
    *   이 보고서는 `stdout`으로 출력됩니다.

6.  **업데이트된 추천 내역 저장 (Save Updated Recommendation History)**
    *   새로운 추천이 추가되고 과거 추천이 검토된 최종 `recommendation_history`를 `recommendation_history.json` 파일에 JSON 형식으로 저장합니다.

이러한 단계들을 거쳐 최종적으로 Altcoin Discovery Project 보고서가 생성되고, Hermes Agent의 `deliver` 메커니즘을 통해 Discord 채널로 전송됩니다.