import fitz
import json

def initialize_structure():
    return {}

def add_chapter(structure, title, chapter_number):
    structure[chapter_number] = {"title": title, "sections": {}}

def add_section(structure, title, chapter_number, section_number):
    if chapter_number not in structure:
        add_chapter(structure, f"Chapter {chapter_number}", chapter_number)
    structure[chapter_number]['sections'][section_number] = {"title": title, "subsections": {}}

def add_subsection(structure, title, chapter_number, section_number, subsection_number):
    if chapter_number in structure and section_number in structure[chapter_number]['sections']:
        structure[chapter_number]['sections'][section_number]['subsections'][subsection_number] = {"title": title}

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Ошибка при открытии PDF: {e}")
        return {}
    
    toc = doc.get_toc()
    structure = initialize_structure()

    current_chapter = None
    current_section = None
    current_subsection = None
    was_chapter = False

    for level, title, page in toc:
        if level == 1:
            if title.startswith("Глава"):
                was_chapter = True
                current_chapter = title.split()[-1]
                continue
            if was_chapter:
                add_chapter(structure, title, current_chapter)
        
        elif level == 2 and current_chapter:
            current_section = title.split()[0]
            if title.strip()[1] == ".":
                add_section(structure, ' '.join(title.split()[1:]), current_chapter, current_section)
        
        elif level == 3 and current_section:
            current_subsection = title.split()[0]
            if title.strip()[1] == ".":
                add_subsection(structure, ' '.join(title.split()[1:]), current_chapter, current_section, current_subsection)

    return structure

def save_structure_to_json(structure, output_path):
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(structure, json_file, ensure_ascii=False, indent=4)

pdf_path = "Руководство_Бухгалтерия_для_Узбекистана_ред_3_0.pdf"
json_output_path = "structure.json"

pdf_structure = extract_text_from_pdf(pdf_path)

save_structure_to_json(pdf_structure, json_output_path)

print(f"Структура успешно сохранена в '{json_output_path}'.")
