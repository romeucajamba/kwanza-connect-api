from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class IEmailService(ABC):
    @abstractmethod
    def send_email(self, subject: str, body: str, recipient: str) -> None:
        pass

class TerminalEmailService(IEmailService):
    """Implementação simples que imprime emails no log/terminal para desenvolvimento."""
    def send_email(self, subject: str, body: str, recipient: str) -> None:
        print("\n" + "="*50)
        print(f"📧 EMAIL ENVIADO PARA: {recipient}")
        print(f"📌 ASSUNTO: {subject}")
        print(f"📝 CORPO:\n{body}")
        print("="*50 + "\n")
        logger.info(f"Email sent to {recipient} with subject: {subject}")
