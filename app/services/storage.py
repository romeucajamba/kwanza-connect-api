from abc import ABC, abstractmethod
from typing import Optional
import io

class IStorageService(ABC):
    """
    Interface para serviços de armazenamento de ficheiros (Cloudinary, S3, Local, etc.)
    """

    @abstractmethod
    def upload(self, file_content: bytes, filename: str, folder: str = "general") -> str:
        """
        Faz upload de um ficheiro e retorna o URL público/seguro.
        :param file_content: Conteúdo do ficheiro em bytes.
        :param filename: Nome sugerido ou ID do ficheiro.
        :param folder: Pasta de destino no serviço.
        :return: URL string.
        """
        pass

    @abstractmethod
    def delete(self, public_id: str) -> None:
        """
        Remove um ficheiro do armazenamento.
        :param public_id: Identificador único do ficheiro no serviço.
        """
        pass
