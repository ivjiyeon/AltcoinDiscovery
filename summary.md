**알트코인 발굴 프로젝트 요약 보고서**

**프로젝트명**: 알트코인 발굴 프로젝트

**목표**:
*   매주 월요일 HKT 08:01 (UTC 00:01)에 Binance.US 현물(Spot) 시장에 상장된 알트코인들의 주봉 차트를 분석하여 1-2주일 내 30% 이상 슈팅할 가능성이 있는 코인 리스트 발굴.
*   분석 결과를 포함한 주간 보고서를 Discord 채널로 자동 발송.
*   지난 주 추천 코인들의 성과를 추적하고 리뷰에 포함.
*   분석 로직 개선 제안 (추후 구현 예정).

**주요 진행 사항**:

1.  **초기 설정**:
    *   프로젝트 시작 및 주간 보고서 자동화 요청 접수.
    *   초기 보고서 수신 채널은 텔레그램으로 설정.
    *   크론잡 `job_id: 9bb1b0f0036a` 생성 (매주 월요일 HKT 08:01 실행).
    *   크론잡의 작업 디렉토리를 `/home/ivjiyeonb/projects/altcoin_discovery`로 설정.

2.  **이메일 발송 시도 및 변경**:
    *   사용자 요청에 따라 이메일 발송을 위해 `himalaya` 스킬 추가 및 크론잡 프롬프트 업데이트.
    *   이메일 수신 실패 확인 후, 보고서 수신 채널을 **Discord 채널 (ID: `1503652607875616859`)** 로 변경.
    *   `himalaya` 관련 이메일 발송 지시 및 스킬 제거.

3.  **파일 정리**:
    *   `/home/ivjiyeonb`에 있던 프로젝트 관련 파일(`get_binance_data_ccxt.py`, `get_binance_data.py`, `analyze_simulated_data.py`, `requirements.txt`)을 `/home/ivjiyeonb/projects/altcoin_discovery` 디렉토리 아래로 이동 및 정리.
    *   스크립트 파일들은 `/home/ivjiyeonb/projects/altcoin_discovery/scripts/`로 이동.

4.  **데이터 소스 및 분석 로직 업데이트**:
    *   Binance API 접근 제한 이슈로 글로벌 바이낸스 선물 데이터 대신 `Binance.US 현물 데이터`를 사용하기로 결정.
    *   `get_binance_data_ccxt.py` 스크립트를 `Binance.US` 현물 데이터 수집용으로 수정.
    *   `analyze_simulated_data.py`를 `analyze_data.py`로 이름 변경.
    *   `coder` 에이전트를 통해 `analyze_data.py`에 다음 분석 로직 구현:
        *   **지표**: RSI, MACD, 볼린저 밴드, Ichimoku Cloud.
        *   **차트 패턴**: 헤드앤숄더, 이중 바닥/천장.
        *   **볼륨 분석**: Accumulation 패턴.
    *   `get_binance_data_ccxt.py`의 출력을 `analyze_data.py`의 입력으로 파이프하여 처리하도록 크론잡 스크립트 수정.

5.  **과거 추천 기록 및 성과 추적 구현**:
    *   보고서에 "추천 코인 리뷰" 및 "로직 업데이트 제안" 부분이 "구현되지 않음"으로 표시되는 문제 확인.
    *   사용자 요청에 따라 `coder` 에이전트를 통해 크론잡 스크립트에 `과거 추천 기록 저장` 및 `성과 추적 로직` 구현 완료.
    *   `/home/ivjiyeonb/projects/altcoin_discovery/recommendation_history.json` 파일에 추천 기록 저장 및 관리.
    *   지난 주 추천 코인들의 30% 슈팅 여부 및 2주 경과 시 포기 로직 구현.
    *   Discord 보고서에 "지난 주 추천 코인 리뷰" 섹션 동적 생성 및 포함 완료.

**현재 상태**:
"알트코인 발굴 프로젝트" 크론잡 (`job_id: bbeb15a5761e`)은 모든 설정이 완료되었으며, 매주 월요일 HKT 08:01에 자동으로 실행되어 Binance.US 현물 데이터를 기반으로 요청하신 분석을 수행하고, 과거 추천 기록을 관리하며, 성과 리뷰가 포함된 주간 보고서를 지정된 Discord 채널 (`1503652607875616859`)로 발송합니다.
