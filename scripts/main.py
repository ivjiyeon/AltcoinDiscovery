import json
from datetime import datetime, timedelta
import pandas as pd # Add pandas for data manipulation

def main(all_current_ohlcv_data, shooting_coins):
    # Define file path for recommendation history
    history_file = "/home/ivjiyeonb/projects/altcoin_discovery/recommendation_history.json"
    recommendation_history = []
    
    # Load existing recommendation history
    try:
        with open(history_file, 'r', encoding='utf-8') as f: # Added encoding='utf-8' for robust handling of file
            recommendation_history = json.load(f)
    except FileNotFoundError:
        pass # File will be created on first save
    except json.JSONDecodeError:
        # Handle corrupted or malformed JSON by resetting history
        print(f"경고: {history_file} 파일이 손상되었거나 형식이 올바르지 않아 초기화합니다.")
        recommendation_history = []

    # --- Performance Tracking and History Management Logic ---
    today_str = datetime.now().strftime("%Y-%m-%d")
    report_reviews = []
    
    updated_history = []
    # Process existing recommendations
    for item in recommendation_history:
        # If the item is already 'shot' or 'abandoned', just add it to the report_reviews for context
        if item['status'] == 'shot':
            report_reviews.append(f"- **{item['coin']}**: ✅ 30% 이상 슈팅 달성! (추천가: {item['recommended_price']:.2f}, 슈팅일: {item['shot_date']})")
        elif item['status'] == 'abandoned':
            report_reviews.append(f"- **{item['coin']}**: ❌ 2주 이내 슈팅 실패, 포기 (추천가: {item['recommended_price']:.2f}, 포기일: {item['abandoned_date']})")
        
        # Only process 'pending' items for status updates
        if item['status'] == 'pending':
            # Check for 30% shoot
            if item['coin'] in all_current_ohlcv_data:
                coin_ohlcv_list = all_current_ohlcv_data.get(item['coin'], [])
                if coin_ohlcv_list:
                    coin_df = pd.DataFrame(coin_ohlcv_list)
                    # Convert 'open_time' to datetime objects. Assuming it's an ISO format string.
                    coin_df['open_time'] = pd.to_datetime(coin_df['open_time']) 
                    rec_datetime = pd.to_datetime(item['recommendation_date']) # This line was moved up
                    
                    # Filter data from recommendation_date onwards to check for high
                    relevant_data_since_rec = coin_df[coin_df['open_time'] >= rec_datetime]
                    
                    if not relevant_data_since_rec.empty:
                        max_high_since_rec = relevant_data_since_rec['high'].max()
                        if max_high_since_rec >= item['recommended_price'] * 1.30:
                            item['status'] = 'shot'
                            item['shot_date'] = today_str
                            report_reviews.append(f"- **{item['coin']}**: ✅ 30% 이상 슈팅 달성! (추천가: {item['recommended_price']:.2f}, 최고가: {max_high_since_rec:.2f})")
            
            # Check for abandonment (2 weeks passed from recommendation date)
            # This check only happens if the coin is *still* pending after the 30% shoot check
            if item['status'] == 'pending':
                rec_date = datetime.strptime(item['recommendation_date'], "%Y-%m-%d")
                if (datetime.now() - rec_date).days >= 14:
                    item['status'] = 'abandoned'
                    item['abandoned_date'] = today_str
                    report_reviews.append(f"- **{item['coin']}**: ❌ 2주 이내 슈팅 실패, 포기 (추천가: {item['recommended_price']:.2f})")
                else:
                    # Still pending, add to review for visibility
                    report_reviews.append(f"- **{item['coin']}**: ⏳ 슈팅 대기 중 (추천가: {item['recommended_price']:.2f}, 추천일: {item['recommendation_date']})")
        
        updated_history.append(item)
    
    # Add new recommendations from current analysis to history
    for coin_data in shooting_coins:
        new_rec = {
            'coin': coin_data['coin'],
            'potential_percent': coin_data['potential_percent'],
            'estimated_target_price': coin_data['estimated_target_price'],
            'recommended_price': coin_data['current_price'], # Use current_price at recommendation time
            'recommendation_date': today_str,
            'status': 'pending'
        }
        # Avoid adding duplicates if the same coin is recommended again while pending
        # This check ensures that if a coin is already pending, we don't add it again.
        # If it was shot/abandoned, it can be re-recommended.
        if not any(item['coin'] == new_rec['coin'] and item['status'] == 'pending' for item in updated_history):
            updated_history.append(new_rec)
    
    recommendation_history = updated_history
    
    # Save updated history
    try:
        with open(history_file, 'w', encoding='utf-8') as f: # Added encoding='utf-8' for Korean characters
            json.dump(recommendation_history, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"경고: 추천 기록 파일을 저장하는 데 실패했습니다: {e}")

    # 3. Format and output the report for Discord
    report_parts = [f"**알트코인 발굴 프로젝트 주간 보고서 ({today_str}) - Binance.US 현물**\\n"]

    if shooting_coins:
        report_parts.append("\\n**새로운 슈팅 가능 코인 리스트:**\\n")
        for coin_data in shooting_coins:
            report_parts.append(f"- **{coin_data['coin']}** (현재가: {coin_data['current_price']:.2f}): 슈팅 가능성 {coin_data['potential_percent']:.2f}%, 예상 타겟가 {coin_data['estimated_target_price']:.2f}\\n")
    else:
        report_parts.append("\\n이번 주에는 슈팅 가능성이 높은 코인이 없습니다.\\n")

    report_parts.append("\\n**지난 주 추천 코인 리뷰:**\\n")
    if report_reviews:
        report_parts.extend([f"{review}\\n" for review in report_reviews])
    else:
        report_parts.append("지난 주 추천 코인 기록이 없습니다.\\n")

    # Placeholder for '로직 업데이트 제안' - will be more sophisticated later
    report_parts.append("\\n**로직 업데이트 제안:**\\n")
    report_parts.append("(이 부분은 아직 구현되지 않았습니다. 지속적인 분석을 통해 로직 개선점을 제안할 예정입니다.)\\n")
    
    return "".join(report_parts) # Return the report instead of printing

if __name__ == "__main__":
    # This block is now empty as the script will be driven by the orchestrator directly calling main() with data
    pass
