import fitz
import json
import re

def load_structure(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        structure = json.load(file)
    return structure

def find_pages_for_structure(pdf_path, structure, start_page=13):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Ошибка при открытии PDF: {e}")
        return {}

    pages = {}
    total_pages = len(doc)

    current_chapter = None
    current_section = None
    current_subsection = None

    for page_number in range(start_page - 1, total_pages):
        page = doc.load_page(page_number)
        text = page.get_text("text")
        lines = text.splitlines()
        combined_text = " ".join(line.strip() for line in lines)

        # Поиск главы
        for chapter_number, chapter_info in structure.items():
            title = chapter_info['title'].upper()
            if re.search(re.escape(title), combined_text) and re.search(re.escape("ГЛАВА"), combined_text):
                if current_chapter and current_chapter in pages:
                    pages[current_chapter]['end_page'] = page_number
                current_chapter = chapter_number
                pages[chapter_number] = {'title': title, 'start_page': page_number + 1, 'end_page': None}

        # Поиск разделов и подразделов внутри текущей главы
        if current_chapter:
            for section_number, section_info in structure[current_chapter]['sections'].items():
                section_title = f"{section_number} {section_info['title']}".upper()
                if re.search(re.escape(section_title), combined_text):
                    if current_section and current_section in pages:
                        pages[current_section]['end_page'] = page_number
                    current_section = section_number
                    pages[section_number] = {'title': section_title, 'start_page': page_number + 1, 'end_page': None}

                # Поиск подразделов
                for subsection_number, subsection_info in section_info['subsections'].items():
                    subsection_title = f"{subsection_number} {subsection_info['title']}"
                    if re.search(re.escape(subsection_title), combined_text, re.IGNORECASE):
                        if current_subsection and current_subsection in pages:
                            pages[current_subsection]['end_page'] = page_number + 1  # Закрываем предыдущий подраздел
                        current_subsection = subsection_number
                        pages[subsection_number] = {'title': subsection_title, 'start_page': page_number + 1, 'end_page': None}

    # Закрытие последней главы, раздела, подраздела
    if current_subsection and current_subsection in pages:
        pages[current_subsection]['end_page'] = total_pages
    if current_section and current_section in pages:
        pages[current_section]['end_page'] = total_pages
    if current_chapter and current_chapter in pages:
        pages[current_chapter]['end_page'] = total_pages

    return pages

def extract_text_for_structure(pdf_path, structure, pages):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Ошибка при открытии PDF: {e}")
        return

    for chapter_number, chapter_info in structure.items():
        if chapter_number in pages:
            start_page = pages[chapter_number]['start_page']
            end_page = pages[chapter_number]['end_page']

            if start_page is not None and end_page is not None:
                chapter_text = []
                for page_number in range(start_page - 1, end_page):
                    page = doc.load_page(page_number)
                    chapter_text.append(page.get_text("text"))
                structure[chapter_number]["text"] = "\n".join(chapter_text)

        # Разделы
        for section_number, section_info in chapter_info['sections'].items():
            if section_number in pages:
                start_page = pages[section_number]['start_page']
                end_page = pages[section_number]['end_page']

                if start_page is not None and end_page is not None:
                    section_text = []
                    for page_number in range(start_page - 1, end_page):
                        page = doc.load_page(page_number)
                        section_text.append(page.get_text("text"))
                    structure[chapter_number]['sections'][section_number]["text"] = "\n".join(section_text)

            # Подразделы
            for subsection_number, subsection_info in section_info['subsections'].items():
                if subsection_number in pages:
                    start_page = pages[subsection_number]['start_page']
                    end_page = pages[subsection_number]['end_page']

                    if start_page is not None and end_page is not None:
                        subsection_text = []
                        for page_number in range(start_page - 1, end_page):
                            page = doc.load_page(page_number)
                            subsection_text.append(page.get_text("text"))
                        structure[chapter_number]['sections'][section_number]['subsections'][subsection_number]["text"] = "\n".join(subsection_text)

def save_structure(output_path, structure):
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(structure, file, ensure_ascii=False, indent=4)
        print(f"Контент успешно сохранена в '{output_path}'.")

json_path = "structure.json"
pdf_path = "Руководство_Бухгалтерия_для_Узбекистана_ред_3_0.pdf"

structure = load_structure(json_path)
pages_with_titles = find_pages_for_structure(pdf_path, structure)
extract_text_for_structure(pdf_path, structure, pages_with_titles)
save_structure(json_path, structure)
