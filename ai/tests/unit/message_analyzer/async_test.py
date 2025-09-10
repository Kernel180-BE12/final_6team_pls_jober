import asyncio
import time

# 모킹 API
async def classify_message_type(user_text: str):
    """메시지 타입 유형 모킹 메서드"""
    await asyncio.sleep(1.5)  # API 응답 1.5초 걸린다고 가정
    return {"type": "예약취소"}

async def classify_message_category(user_text: str, category_main: str, category_sub_list: list):
    """메시지 타입 유형 모킹 메서드"""
    await asyncio.sleep(2.0)  # API 응답 2초 걸린다고 가정
    return {"category_sub": "구매취소"}

async def extract_message_fields(user_text: str, fields_hint: list):
    """메시지 타입 유형 모킹 메서드"""
    await asyncio.sleep(0.8)  # 필드 추출 0.8초 걸린다고 가정
    return {"fields": {"주문번호": "12345"}}

# 순차 실행 테스트와 병렬 실행 테스트 비교
async def sequential_analyze(user_text: str, category_main: str, category_sub_list: list):
    """순차 실행 테스트"""
    start = time.perf_counter()
    type_result = await classify_message_type(user_text)
    category_result = await classify_message_category(user_text, category_main, category_sub_list)
    extract_result = await extract_message_fields(user_text, [])
    combined = {**type_result, **category_result, **extract_result}
    end = time.perf_counter()
    print(f"⏱ [순차 실행] 총 실행 시간: {end - start:.2f}초")
    return combined


# 병렬 실행 (asyncio.gather)
async def parallel_analyze(user_text: str, category_main: str, category_sub_list: list):
    """병렬 실행 테스트"""
    start = time.perf_counter()
    type_result, category_result = await asyncio.gather(
        classify_message_type(user_text),
        classify_message_category(user_text, category_main, category_sub_list)
    )
    extract_result = await extract_message_fields(user_text, [])
    combined = {**type_result, **category_result, **extract_result}
    end = time.perf_counter()
    print(f"⚡ [병렬 실행] 총 실행 시간: {end - start:.2f}초")
    return combined


# 테스트 실행
async def main():
    user_text = "예약을 취소하고 싶어요"
    category_main = "주문"
    category_sub_list = ["예약취소", "환불요청"]

    print("=============== 성능 벤치마크 시작 =============== ")
    await sequential_analyze(user_text, category_main, category_sub_list)
    await parallel_analyze(user_text, category_main, category_sub_list)

asyncio.run(main())