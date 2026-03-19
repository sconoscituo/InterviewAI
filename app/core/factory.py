"""
팩토리 패턴 - 서비스 인스턴스 생성 및 싱글톤 관리
헥사고날 아키텍처의 컴포지션 루트 역할
"""
from typing import Type, TypeVar, Dict, Any

T = TypeVar("T")

_instances: Dict[type, Any] = {}


class ServiceFactory:
    """서비스 싱글톤 팩토리"""

    @classmethod
    def get_instance(cls, service_class: Type[T]) -> T:
        """싱글톤 인스턴스 반환 - 없으면 생성"""
        if service_class not in _instances:
            _instances[service_class] = service_class()
        return _instances[service_class]

    @classmethod
    def clear(cls) -> None:
        """테스트용 인스턴스 초기화"""
        _instances.clear()

    # --- InterviewAI 전용 팩토리 메서드 ---

    @classmethod
    def create_question_generator(cls):
        """면접 질문 생성 서비스 인스턴스 반환"""
        from app.services.question_generator import generate_questions
        return generate_questions

    @classmethod
    def create_evaluator(cls):
        """답변 평가 서비스 인스턴스 반환"""
        from app.services.evaluator import evaluate_answer
        return evaluate_answer

    @classmethod
    def create_payment_service(cls):
        """결제 서비스 인스턴스 반환"""
        from app.services import payment
        return payment

    @classmethod
    def create_subscription_service(cls):
        """구독 서비스 인스턴스 반환"""
        from app.services import subscription
        return subscription
