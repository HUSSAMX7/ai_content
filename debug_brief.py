"""مخرجات debug/عرض المقابلة في الطرفية (CLI) — منفصل عن منطق الـ workflow."""


def format_requirements_brief_ar(memo: str) -> str:
    """تنسيق مذكرة المتطلبات لعرضها في الطرفية."""
    m = (memo or "").strip()
    if not m:
        return "  مذكرة المتطلبات: (فارغة)"
    return f"  مذكرة المتطلبات:\n{m}"


def format_clean_requirements_brief_ar(clean: str) -> str:
    """تنسيق المتطلبات المصفّاة لعرضها في الطرفية."""
    c = (clean or "").strip()
    if not c:
        return "  المتطلبات المصفّاة: (فارغة)"
    return f"  المتطلبات المصفّاة:\n{c}"
