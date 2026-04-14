import cloudinary.uploader
from .storage import IStorageService

class CloudinaryStorageService(IStorageService):
    """
    Implementação do IStorageService utilizando a SDK do Cloudinary.
    """

    def upload(self, file_content: bytes, filename: str, folder: str = "general") -> str:
        """
        Faz upload de um buffer de bytes para o Cloudinary.
        """
        result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            public_id=filename,
            overwrite=True,
            resource_type="auto"
        )
        return result.get('secure_url')

    def delete(self, public_id: str) -> None:
        """
        Remove a imagem do Cloudinary.
        """
        cloudinary.uploader.destroy(public_id)
