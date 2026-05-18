"""
فرمت‌کننده‌های سراسری اپلیکیشن مصباح
"""

_persian_digits = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def persian_numbers(text) -> str:
    """تبدیل اعداد انگلیسی به فارسی - برای استفاده در سراسر پروژه"""
    if text is None:
        return ""
    return str(text).translate(_persian_digits)
