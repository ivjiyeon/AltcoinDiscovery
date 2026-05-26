import json
import datetime
import os
import sys


# Assuming default_api is available in the execution environment of this script
# when run as a cron job by the Hermes Agent.
# If not, this script would need to be executed in a context where default_api is injected.

PROJECT_ROOT = "/home/ivjiyeonb/projects/altcoin_discovery"
VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv/bin/python")
GET_BINANCE_DATA_SCRIPT = os.path.join(PROJECT_ROOT, "scripts/get_binance_data_ccxt.py")
ANALYZE_DATA_SCRIPT = os.path.join(PROJECT_ROOT, "scripts/analyze_data.py")
RECOMMENDATION_HISTORY_FILE = os.path.join(PROJECT_ROOT, "data/recommendation_history.json")



def run_cron_job():
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")

    # 1. Execute data acquisition and analysis
    command = f"{VENV_PYTHON} {GET_BINANCE_DATA_SCRIPT} | {VENV_PYTHON} {ANALYZE_DATA_SCRIPT}"
    print(f"Running command: {command}")
    # Using default_api directly as per the instruction "Use hermes_tools.terminal..."
    # implies default_api or a wrapper for it is available.
    analysis_output = default_api.terminal(command=command, workdir=PROJECT_ROOT)

    if analysis_output['exit_code'] != 0:
        print(f"Error running analysis scripts: {analysis_output['output']}")
        return

    try:
        analysis_data = json.loads(analysis_output['output'])
        new_recommendations = analysis_data.get("new_recommendations", [])
        current_prices = analysis_data.get("current_prices", {})
        # If analyze_data.py output is just a list of recommendations, handle it.
        if isinstance(analysis_data, list):
            new_recommendations = analysis_data
            print("Warning: analyze_data.py output was a list. Assuming no current_prices were provided for historical review.")
            # In this case, current_prices will remain empty, affecting past recommendation review.
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from analysis script output: {e}")
        print(f"Output: {analysis_output['output']}")
        return

    # 2. Load existing recommendation history
    history_content_response = default_api.read_file(RECOMMENDATION_HISTORY_FILE)
    recommendation_history = []
    if history_content_response and history_content_response.get("content") is not None:
        try:
            recommendation_history = json.loads(history_content_response["content"])
        except json.JSONDecodeError:
            print(f"Error decoding {RECOMMENDATION_HISTORY_FILE}. Starting with empty history.")
    else:
        print(f"{RECOMMENDATION_HISTORY_FILE} not found or empty. Starting with empty history.")

    # 3. Process new recommendations
    for rec in new_recommendations:
        rec["recommendation_date"] = today_str
        recommendation_history.append(rec)

    # 4. Review past recommendations
    updated_history = []
    report_hit = []
    report_abandoned = []

    for rec in recommendation_history:
        rec_date = datetime.datetime.strptime(rec["recommendation_date"], "%Y-%m-%d").date()
        days_since_rec = (today - rec_date).days

        coin_symbol = rec["coin"]
        current_coin_price = current_prices.get(coin_symbol)

        if current_coin_price is None:
            # Cannot review this coin if current price is unknown. Keep it in history.
            updated_history.append(rec)
            continue

        # Check for target hit (30% gain)
        target_hit = False
        if current_coin_price >= rec["current_price"] * 1.30: # 30% or more above original current_price
            report_hit.append({
                "coin": rec["coin"],
                "original_price": rec["current_price"],
                "current_price": current_coin_price,
                "recommendation_date": rec["recommendation_date"]
            })
            target_hit = True
            # Do not add to updated_history as it has hit its target

        # Check for abandonment if not hit target and outstanding for > 2 weeks (14 days)
        elif days_since_rec > 14:
            report_abandoned.append({
                "coin": rec["coin"],
                "original_price": rec["current_price"],
                "current_price": current_coin_price,
                "recommendation_date": rec["recommendation_date"]
            })
            # Do not add to updated_history as it is abandoned
        else:
            # If not hit target and not abandoned, keep in history
            updated_history.append(rec)

    recommendation_history = updated_history

    # 5. Generate Discord report
    report_lines = [
        f"--- 알트코인 추천 보고서 - {today_str} ---",
        "",
        "## 프로젝트 목표",
        "알트코인 시장에서 잠재력 있는 코인을 자동으로 탐지하고, 투자 기회를 식별하여 사용자에게 추천합니다. 과거 추천 코인들의 성능을 추적하고, 시장 변화에 따라 추천 전략을 최적화합니다.",
        ""
    ]

    if new_recommendations:
        report_lines.append("## 신규 추천 코인:")
        for rec in new_recommendations:
            report_lines.append(f"- **{rec['coin']}**: 현재 가격 {rec['current_price']:.4f} USD, 잠재력 {rec['potential_percent']:.2f}%, 예상 목표가 {rec['estimated_target_price']:.4f} USD")
        report_lines.append("")
    else:
        report_lines.append("## 신규 추천 코인: 없음")
        report_lines.append("")

    if report_hit or report_abandoned:
        report_lines.append("## 과거 추천 코인 검토:")
        if report_hit:
            report_lines.append("### ✅ 목표 달성 코인:")
            for rec in report_hit:
                report_lines.append(f"- **{rec['coin']}** (추천일: {rec['recommendation_date']}): 추천 당시 {rec['original_price']:.4f} USD -> 현재 {rec['current_price']:.4f} USD")
        if report_abandoned:
            report_lines.append("### ❌ 포기된 코인 (2주 이상 미달성):")
            for rec in report_abandoned:
                report_lines.append(f"- **{rec['coin']}** (추천일: {rec['recommendation_date']}): 추천 당시 {rec['original_price']:.4f} USD -> 현재 {rec['current_price']:.4f} USD")
        report_lines.append("")
    else:
        report_lines.append("## 과거 추천 코인 검토: 해당 사항 없음")
        report_lines.append("")

    discord_report = "\n".join(report_lines)
    print(discord_report)


    # 6. Save updated recommendation history
    default_api.write_file(RECOMMENDATION_HISTORY_FILE, json.dumps(recommendation_history, indent=4, ensure_ascii=False))
    print(f"Updated {RECOMMENDATION_HISTORY_FILE}")

# Main execution block
if __name__ == "__main__":
    run_cron_job()