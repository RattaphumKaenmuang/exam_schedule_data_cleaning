# %%
import pandas as pd

def convert_exam_report(file_path: str) -> pd.DataFrame:
    """
    Read the exam report file (.xls) from file_path
    and return it as a pandas DataFrame in the specified format.
    """

    df = pd.read_excel(file_path, header=None)
    pages_idx = []

    for i, row in df.iterrows():
        if "ลำดับ" in str(row):
            pages_idx.append(i)
    
    new_df = build_df_from_pages(df, pages_idx)

    return new_df

def build_df_from_pages(df: pd.DataFrame, pages_idx: list) -> pd.DataFrame:
    """
    Create a new DataFrame from the DataFrame read from the exam report file
    using the page indices (pages_idx) to separate the data into each page.
    """

    ex_date = process_exam_date_str(get_exam_date_str(df))

    # [DONE] order — ลำดับวิชา จากคอลัมน์ "ลำดับ" ถ้าวิชาหนึ่งสอบพร้อมกันหลายห้อง แถวที่ 2 เป็นต้นไปของวิชานั้นในไฟล์ต้นฉบับจะว่าง ต้องเติมค่าจากแถวแรกของวิชานั้นให้ครบ (forward fill)
    # [DONE] subj — รหัสวิชา + ชื่อวิชา จากคอลัมน์ "วิชา" ต้อง forward fill เช่นเดียวกับ order
    # [DONE] sec — กลุ่มเรียน จากคอลัมน์ "กลุ่ม"
    # [DONE] st_year — ชั้นปี จากคอลัมน์ "ชั้นปี"
    # [DONE] st_max — จำนวนนักศึกษาทั้งหมดในกลุ่ม จากคอลัมน์ "นศ."
    # [DONE] ex_dur — ช่วงเวลาสอบ จากคอลัมน์ "เวลา" เช่น 09:30:00 - 12:30:00
    # [DONE] teacher_str — รายชื่อผู้สอนตามที่ปรากฏในไฟล์ต้นฉบับ (คำนำหน้าตำแหน่งวิชาการครบ คั่นด้วย ,) จากคอลัมน์ "ผู้สอน"
    # [DONE] building — อาคารที่สอบ จากคอลัมน์ "อาคาร"
    # [DONE] room — ห้องสอบ จากคอลัมน์ "ห้อง"
    # [DONE] note — จำนวนนักศึกษาที่สอบจริง/ที่นั่งในห้องนั้น เช่น 36/36 จากคอลัมน์ "หมายเหตุ"
    # [DONE] ex_date — วันที่สอบ รูปแบบ YYYY-MM-DD (ปี ค.ศ.) ดึงจากข้อความหัวรายงาน "วันสอบ ..." (มีบอกวันที่แบบ พ.ศ. และเดือนย่อภาษาไทย ต้องแปลงเป็น ค.ศ. และเลขเดือน)
    # [DONE] code4 — รหัสวิชา 4 หลักแรก (ตัวเลข) ตัด 4 ตัวแรกของรหัสวิชาใน subj
    # [DONE] ex_time — ชั่วโมงเริ่มสอบ (ตัวเลข) ดึงชั่วโมงเริ่มจาก ex_dur
    # [DONE] st_num — จำนวนนักศึกษาที่สอบจริงในห้องนั้น (ตัวเลข) คือตัวเลขก่อนเครื่องหมาย / ใน note ถ้าไม่มีห้องสอบ/ไม่มีค่า ให้เป็น 0
    # [DONE] ex_dt — วันเวลาสอบแบบย่อ รวมไว้ใช้ group/sort คือ - ex_date + เว้นวรรค + ex_time เช่น 2026-03-19 13
    # [DONE] teachers — รายชื่อผู้สอน ตัดคำนำหน้าตำแหน่งวิชาการออก (เช่น ผศ., ดร., รศ., ผศ. ดร., รศ. ดร., ศ., อ. ฯลฯ) และคั่นหลายคนด้วย ; แทน , ประมวลผลจาก teacher_str

    rows = []
    for i in range(len(pages_idx)):
        start_idx = pages_idx[i] + 1

        # Ends when the entire row is NaN, when the next page starts, or when the data ends.
        if i + 1 < len(pages_idx):
            end_idx = pages_idx[i + 1]
        else:
            end_idx = len(df)
        
        order = None
        subj = None

        for j in range(start_idx, end_idx):
            row = df.iloc[j]
            if row.isnull().all(): break

            order =         str(row[0]) if not is_cell_empty(row[0]) else order
            subj =          str(row[1]) if not is_cell_empty(row[1]) else subj
            sec =           str(row[2]) if not is_cell_empty(row[2]) else None
            st_year =       str(row[3]) if not is_cell_empty(row[3]) else None
            st_max =        str(row[4]) if not is_cell_empty(row[4]) else None
            ex_dur =        str(row[5]) if not is_cell_empty(row[5]) else None
            teacher_str =   str(row[6]) if not is_cell_empty(row[6]) else None
            building =      str(row[7]) if not is_cell_empty(row[7]) else None
            room =          str(row[8]) if not is_cell_empty(row[8]) else None
            note =          str(row[9]) if not is_cell_empty(row[9]) else None
            # ex_date already processed above.
            code4 =         str(subj)[:4] if subj else None
            ex_time =       ex_dur[:2] if ex_dur else None
            st_num =        int(note.split('/')[0]) if pd.notna(note) and room != ' ' else 0
            ex_dt =         f"{ex_date} {ex_time}" if ex_date and ex_time else None
            teachers =      process_teachers_str(teacher_str)

            rows.append({
                "order": order,
                "subj": subj,
                "sec": sec,
                "st_year": st_year,
                "st_max": st_max,
                "ex_dur": ex_dur,
                "teacher_str": teacher_str,
                "building": building,
                "room": room,
                "note": note,
                "ex_date": ex_date,
                "code4": code4,
                "ex_time": ex_time,
                "st_num": st_num,
                "ex_dt": ex_dt,
                "teachers": teachers
            })

    return pd.DataFrame(rows)

def get_exam_date_str(df: pd.DataFrame) -> str:
    """
    Extract raw exam date string from the DataFrame (df) read from the exam report file.
    """

    exam_date_str = ""
    for _, row in df.iterrows():
        for cell in row:
            if "วันสอบ" in str(cell):
                exam_date_str = str(cell)
                break

    return exam_date_str

def process_exam_date_str(exam_date_str: str) -> str:
    """
    Process the raw exam date string to extract the exam date.
    Returns the processed exam date string.
    """

    # Time columns to extract:
    # [DONE] ex_dur — ช่วงเวลาสอบ จากคอลัมน์ "เวลา" เช่น 09:30:00 - 12:30:00
    # [DONE] ex_date — วันที่สอบ รูปแบบ YYYY-MM-DD (ปี ค.ศ.) ดึงจากข้อความหัวรายงาน "วันสอบ ..." (มีบอกวันที่แบบ พ.ศ. และเดือนย่อภาษาไทย ต้องแปลงเป็น ค.ศ. และเลขเดือน)
    # [DONE] ex_time — ชั่วโมงเริ่มสอบ (ตัวเลข) ดึงชั่วโมงเริ่มจาก ex_dur
    # [DONE] ex_dt — วันเวลาสอบแบบย่อ รวมไว้ใช้ group/sort คือ - ex_date + เว้นวรรค + ex_time เช่น 2026-03-19 13

    months = {
        "ม.ค.": "01",
        "ก.พ.": "02",
        "มี.ค.": "03",
        "เม.ย.": "04",
        "พ.ค.": "05",
        "มิ.ย.": "06",
        "ก.ค.": "07",
        "ส.ค.": "08",
        "ก.ย.": "09",
        "ต.ค.": "10",
        "พ.ย.": "11",
        "ธ.ค.": "12"
    }

    exam_date_parts = exam_date_str.split()                 # ['วันสอบ', 'จ.', '16', 'มี.ค.', '69', 'เวลา', '13:00-16:30', 'น.']

    day = exam_date_parts[2]                                # '16'
    month_str = exam_date_parts[3]                          # 'มี.ค.'
    buddhist_year_str = exam_date_parts[4]                  # '69'

    month = months[month_str]                               # '03'
    gregorian_year = int(buddhist_year_str) + 2500 - 543    # '2026'

    ex_date = f"{gregorian_year}-{month}-{day}"

    return ex_date

def process_teachers_str(teacher_str: str | None) -> str:
    """
    Process the teacher string to remove academic titles and format it.
    Returns the processed teacher string.
    """

    teachers_list = [t.strip() for t in teacher_str.split(',')] if pd.notna(teacher_str) else []
    # Steps backwards until the first dot is found.
    for i in range(len(teachers_list)):
        t = teachers_list[i]

        # Very funny, อาจารย์SUSHISH BARAL
        # Check for English alphabet in case someone named อาจารย์ actually shows up (please don't)
        foreign_name = t.split('อาจารย์')[-1]
        if 'อาจารย์' in t and (foreign_name[0].isalpha() or foreign_name[0] == ' '):
            teachers_list[i] = t.split('อาจารย์')[-1].strip()
            continue

        for j in range(len(t) - 1, -1, -1):
            if t[j] == '.':
                teachers_list[i] = t[j + 1:].strip()
                break
    teachers = '; '.join(teachers_list)

    return teachers

def is_cell_empty(cell) -> bool:
    """
    Check if a cell is empty (NaN or whitespace).
    Returns True if the cell is empty, False otherwise.
    """

    return pd.isna(cell) or str(cell).strip() == '' or str(cell) == ' '

df = convert_exam_report("16 เช้า.xls")

# %%