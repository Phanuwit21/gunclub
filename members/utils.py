"""Utility functions สำหรับ members app."""

import base64
import io


def generate_qr_base64(url, size=120):
    """
    สร้าง QR Code เป็น base64 data URL
    ถ้าสร้างไม่ได้ return None (ใช้ fallback ไป api.qrserver.com)

    Args:
        url: URL ที่ต้องการ encode เป็น QR
        size: ขนาด pixel ของ QR (default 120)

    Returns:
        str: "data:image/png;base64,xxx" หรือ None ถ้าเกิด error
    """
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except Exception:
        return None
