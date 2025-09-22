from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

async def validation_exception_handler(request, exc: RequestValidationError):
    """
    Pydantic 모델 유효성 검사 실패 시, 더 자세한 오류 로그를 출력하기 위한 핸들러.
    :param request:
    :param exc:
    :return:
    """
    print("\n" + "="*50)
    print("🕵️‍♂️ 422 Validation Error 발생! 🕵️‍♂️")
    print("클라이언트가 보낸 요청 데이터가 Pydantic 모델과 일치하지 않습니다.")
    print("자세한 오류 내용:")
    # exc.errors()는 오류에 대한 상세 정보를 담고 있는 리스트입니다.
    print(exc.errors())
    print("="*50 + "\n")

    errors = []
    for err in exc.errors():
        errors.append({
            "field": err["loc"][-1],
            "message": err["msg"],
            "type": err["type"],
        })
    # 클라이언트에게도 상세 오류 정보를 반환합니다.
    return JSONResponse(
        status_code=422,
        content={
            "code": "INVALID_INPUT",
            "errors": errors
        }
    )