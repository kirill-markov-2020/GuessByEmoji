from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GigaChatHelper:
    def __init__(self, credentials: str):
        """
        Инициализация GigaChat с вашими учетными данными.
        :param credentials: Ваш токен авторизации GigaChat
        """
        try:
            self.giga = GigaChat(credentials=credentials, verify_ssl_certs=False)
            logger.info("GigaChat успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации GigaChat: {e}")
            raise

    def compare_answers(self, user_answer: str, correct_answer: str) -> bool:
        """
        Сравнивает ответ пользователя с правильным ответом с помощью GigaChat.
        :param user_answer: Ответ пользователя
        :param correct_answer: Правильный ответ из базы данных
        :return: True, если ответ считается верным, иначе False
        """
        try:
            prompt = (
                f"Сравни ответ пользователя с правильным ответом и определи, можно ли считать их схожими по смыслу.\n"
                f"Правильный ответ: '{correct_answer}'\n"
                f"Ответ пользователя: '{user_answer}'\n"
                "Ответь только 'да' или 'нет' без пояснений."
            )

            chat = Chat(
                messages=[
                    Messages(
                        role=MessagesRole.SYSTEM,
                        content="Ты помощник, который сравнивает ответы пользователей с правильными ответами."
                    ),
                    Messages(
                        role=MessagesRole.USER,
                        content=prompt
                    )
                ],
                temperature=0.1
            )

            # Отправляем запрос
            response = self.giga.chat(chat)
            response_text = response.choices[0].message.content.lower().strip()

            logger.info(f"GigaChat response: {response_text}")

            return response_text == "да"

        except Exception as e:
            logger.error(f"Ошибка при сравнении ответов: {e}")
            return False