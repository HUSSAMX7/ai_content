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


def print_analyzed_template_chapters(chapters: list[dict[str, str]]) -> None:
    """طباعة الفصول المستخرجة من التمبلت (debug CLI)."""
    print("\n" + "═" * 60)
    print("  [analyze_template] استخراج الفصول من التمبلت")
    print(f"  عدد الفصول: {len(chapters)}")
    print("═" * 60)
    for i, ch in enumerate(chapters, start=1):
        title = ch.get("title", "")
        desc = ch.get("description", "")
        print(f"\n── فصل {i} ──")
        print(f"العنوان: {title}")
        print("الوصف / التعليمات:")
        print(desc if desc.strip() else "(فارغ)")
    print("\n" + "═" * 60 + "\n")
