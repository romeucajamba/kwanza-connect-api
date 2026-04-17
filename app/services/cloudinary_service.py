import cloudinary.uploader
from .storage import IStorageService

class CloudinaryStorageService(IStorageService):
    """
    Implementação do serviço de armazenamento utilizando Cloudinary.
    """

    def upload(self, file_content: bytes, filename: str, folder: str = "general") -> str:
        """
        Faz upload para o Cloudinary e retorna o URL seguro.
        """
        try:
            upload_result = cloudinary.uploader.upload(
                file_content,
                public_id=filename,
                folder=f"kwanzaconnect/{folder}",
                overwrite=True,
                resource_type="auto"
            )
            return upload_result.get('secure_url')
        except Exception as e:
            # Em caso de erro, poderíamos fazer log. 
            # Para o MVP, relançamos ou retornamos erro.
            raise Exception(f"Erro no upload para Cloudinary: {str(e)}")

    def delete(self, public_id: str) -> None:
        """
        Remove do Cloudinary.
        """
        try:
            cloudinary.uploader.destroy(public_id)
        except Exception:
            pass
