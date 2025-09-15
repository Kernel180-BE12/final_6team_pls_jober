import asyncio
import time
import pytest

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


# pytest 테스트 함수들
@pytest.mark.asyncio
async def test_classify_message_type():
    """메시지 타입 분류 테스트"""
    result = await classify_message_type("예약을 취소하고 싶어요")
    assert result["type"] == "예약취소"

@pytest.mark.asyncio
async def test_classify_message_category():
    """메시지 카테고리 분류 테스트"""
    result = await classify_message_category("예약을 취소하고 싶어요", "주문", ["예약취소", "환불요청"])
    assert result["category_sub"] == "구매취소"

@pytest.mark.asyncio
async def test_extract_message_fields():
    """메시지 필드 추출 테스트"""
    result = await extract_message_fields("예약을 취소하고 싶어요", [])
    assert "fields" in result
    assert "주문번호" in result["fields"]

@pytest.mark.asyncio
async def test_sequential_analyze():
    """순차 실행 성능 테스트"""
    user_text = "예약을 취소하고 싶어요"
    category_main = "주문"
    category_sub_list = ["예약취소", "환불요청"]
    
    result = await sequential_analyze(user_text, category_main, category_sub_list)
    
    # 결과 검증
    assert result["type"] == "예약취소"
    assert result["category_sub"] == "구매취소"
    assert "fields" in result

@pytest.mark.asyncio
async def test_parallel_analyze():
    """병렬 실행 성능 테스트"""
    user_text = "예약을 취소하고 싶어요"
    category_main = "주문"
    category_sub_list = ["예약취소", "환불요청"]
    
    result = await parallel_analyze(user_text, category_main, category_sub_list)
    
    # 결과 검증
    assert result["type"] == "예약취소"
    assert result["category_sub"] == "구매취소"
    assert "fields" in result

@pytest.mark.asyncio
async def test_parallel_vs_sequential_performance():
    """병렬 실행과 순차 실행 성능 비교 테스트"""
    user_text = "예약을 취소하고 싶어요"
    category_main = "주문"
    category_sub_list = ["예약취소", "환불요청"]
    
    # 순차 실행 시간 측정
    start = time.perf_counter()
    await sequential_analyze(user_text, category_main, category_sub_list)
    sequential_time = time.perf_counter() - start
    
    # 병렬 실행 시간 측정
    start = time.perf_counter()
    await parallel_analyze(user_text, category_main, category_sub_list)
    parallel_time = time.perf_counter() - start
    
    # 병렬 실행이 더 빠른지 확인 (최소 0.5초 이상 차이)
    assert parallel_time < sequential_time - 0.5, f"병렬 실행({parallel_time:.2f}s)이 순차 실행({sequential_time:.2f}s)보다 충분히 빠르지 않습니다"