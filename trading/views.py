from django.shortcuts import render, redirect
import mojito
from django.http import JsonResponse
from login.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dotenv import load_dotenv
import json
from django.views.decorators.csrf import csrf_exempt

load_dotenv()


@csrf_exempt  # CSRF 비활성화 (테스트 용도)
def place_order(request):
    # 현재 로그인한 사용자의 UserProfile 가져오기
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # UserProfile이 없는 경우 에러 처리
        return JsonResponse({'message': '사용자 프로필을 찾을 수 없습니다.'}, status=400)

    # 한국투자 API 연결
    broker = mojito.KoreaInvestment(
        api_key=user_profile.api_key,
        api_secret=user_profile.api_secret,
        acc_no=user_profile.acc_num,  # 계좌 번호
        exchange='나스닥',  # 애플 주식을 구매할 때 사용 (NASDAQ)
        mock=True  # 모의 투자 모드
    )

    if request.method == "POST":
        try:
            # JSON 요청 데이터를 파싱
            data = json.loads(request.body)
            stock_code = data.get('stock_code')
            price = float(data.get('price'))
            quantity = int(data.get('quantity', 1))  # 기본 수량은 1로 설정

            if price is None or quantity is None or stock_code is None:
                return JsonResponse({'message': '필수 매개변수가 누락되었습니다.'}, status=400)

            # 주문 실행
            response = broker.create_oversea_order(
                side='buy',  # 매수
                symbol=stock_code,  # 주식 코드
                price=price,  # 지정가
                quantity=quantity,  # 수량
                order_type="00"  # 00은 지정가 주문
            )

            print(response)
            # 주문 응답 처리
            if response.get('rt_cd') == '0' and '모의투자 매수주문이 완료 되었습니다.' in response.get('msg1', ''):
                return JsonResponse({'message': 'complete'})
            else:
                err_message = response.get('msg1', 'Unknown error')
                return JsonResponse({'message': f'failed: {err_message}'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print(f"Error occurred: {e}")
            return JsonResponse({'message': f'error: {str(e)}'}, status=400)

        return JsonResponse({'message': 'Invalid request method'}, status=405)


def trading(request):
    return render(request, 'trading/trading.html')