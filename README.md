# Gun Club Membership System

ระบบจัดการสมาชิก Gun Club สร้างด้วย Django

## ความต้องการของระบบ

- Python 3.10+
- Django 6.x
- Pillow (สำหรับอัปโหลดรูปภาพ)

## การติดตั้ง

### 1. Clone และเข้าโฟลเดอร์โปรเจกต์

```bash
cd gunclub_system
```

### 2. สร้าง Virtual Environment

```bash
python -m venv venv
```

### 3. เปิดใช้ Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 5. รัน Migration

```bash
python manage.py migrate
```

### 6. สร้างบัญชี Admin (Superuser)

```bash
python manage.py createsuperuser
```

### 7. รันเซิร์ฟเวอร์

```bash
python manage.py runserver
```

เปิดเบราว์เซอร์ที่ http://127.0.0.1:8000/

## การตั้งค่า Environment (ไม่บังคับ)

สร้างไฟล์ `.env` จาก `.env.example` เพื่อกำหนดค่า:

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
SITE_URL=http://127.0.0.1:8000
TIME_ZONE=Asia/Bangkok
LANGUAGE_CODE=th
```

## Roles

- **MEMBER** — สมาชิกทั่วไป ดูและแก้โปรไฟล์ตัวเองได้
- **STAFF** — จัดการสมาชิก, แดชบอร์ด
- **COMMITTEE** — เหมือน Staff + สร้างบัญชี Staff ได้
- **PRESIDENT** — สิทธิ์เต็ม

## หมายเหตุ

- สมาชิกใหม่ที่สร้างจาก Add Member จะได้รหัสผ่านสุ่ม — แสดงครั้งเดียวหลังสร้าง ให้บันทึกและส่งให้สมาชิก
- ลิงก์ลืมรหัสผ่านใช้กับ User ที่มีอีเมลในระบบ ในโหมด dev อีเมลจะแสดงใน Console
