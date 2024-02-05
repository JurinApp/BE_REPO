from datetime import datetime

from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image

from jurin.common.exception.exceptions import ValidationException
from jurin.files.utils import bytes_to_mib


class FileUploadService:
    def __init__(self, file_obj, channel_id: int):
        self.channel_id = channel_id
        self.file_obj = file_obj

    def _validate_file_size(self):
        """
        이 함수는 파일의 크기가 설정된 최대 크기를 넘지 않는지 확인합니다. (10MB)
        """
        max_size = settings.FILE_MAX_SIZE
        file_size = len(self.file_obj.read())

        if file_size > max_size:
            raise ValidationException(f"File is too large. It should not exceed {bytes_to_mib(max_size)} MiB")

    def _validate_file_type(self):
        """
        이 함수는 파일의 타입이 이미지인지 확인합니다.
        """
        try:
            file = Image.open(self.file_obj)
            file.verify()

        except Exception as e:
            raise ValidationException(f"Invalid file type: {e}")

    def _get_resource_path(self) -> str:
        """
        이 함수는 파일을 업로드할 경로를 반환합니다.
        Returns:
            resource_path(str): 파일을 업로드할 경로
        """
        id_path = str(self.channel_id)
        ext = str(self.file_obj.name).split(".")[-1]

        resource_path = "channels/" + id_path + "/items/" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f") + "." + ext

        return resource_path

    def upload_file(self) -> str:
        """
        이 파일을 검증하고 AWS S3에 업로드합니다.

        Returns:
            file_url(str): 업로드된 파일의 URL
        """
        try:
            # 파일 크기 검증
            self._validate_file_size()

            # 파일 타입 검증
            self._validate_file_type()

            # 파일 업로드 경로 설정
            upload_path = self._get_resource_path()

            # 파일 업로드
            default_storage.save(upload_path, self.file_obj)

            return settings.AWS_S3_URL + "/" + upload_path

        except Exception as e:
            raise ValidationException(str(e))
