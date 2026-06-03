from io import BytesIO

import qrcode


class QRService:
    @staticmethod
    def build_qr_image_bytes(link: str) -> BytesIO:
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)

        image = qr.make_image(fill_color="black", back_color="white")

        output = BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        return output
