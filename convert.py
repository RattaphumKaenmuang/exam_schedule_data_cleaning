# %%
import pandas as pd

def convert_exam_report(file_path: str) -> pd.DataFrame:
    """
    Read the exam report file (.xls) from file_path
    and return it as a pandas DataFrame in the specified format.
    """
    ...

    df = pd.read_excel(file_path, header=None)
    pages_idx = []

    for i, row in df.iterrows():
        if "ลำดับ" in str(row):
            pages_idx.append(i)
    
    build_df_from_pages(df, pages_idx)

    return df

def build_df_from_pages(df: pd.DataFrame, pages_idx: list) -> pd.DataFrame:
    """
    Create a new DataFrame from the DataFrame read from the exam report file
    using the page indices (pages_idx) to separate the data into each page.
    """
    ...

    new_df = pd.DataFrame(columns=[
        "order",
        "subj",
        "sec",
        "st_year",
        "st_max",
        "ex_dur",
        "teacher_str",
        "building",
        "room",
        "note",
        "ex_date",
        "code4",
        "ex_time",
        "st_num",
        "ex_dt",
        "teachers"
    ])

    ex_dur, ex_date, ex_time, ex_dt = process_exam_date_str(get_exam_date_str(df))

    return new_df

def get_exam_date_str(df: pd.DataFrame) -> str:
    """
    Extract raw exam date string from the DataFrame (df) read from the exam report file.
    """
    ...

    exam_date_str = ""
    for _, row in df.iterrows():
        for cell in row:
            if "วันสอบ" in str(cell):
                exam_date_str = str(cell)

    return exam_date_str

def process_exam_date_str(exam_date_str: str) -> tuple:
    """
    Process the raw exam date string to extract the exam date and time components.
    Returns a tuple containing (ex_dur, ex_date, ex_time, ex_dt).
    """
    ...

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

    exam_date_str = get_exam_date_str(df)                   # วันสอบ  จ. 16 มี.ค. 69 	เวลา 13:00-16:30 น.
    exam_date_parts = exam_date_str.split()                 # ['วันสอบ', 'จ.', '16', 'มี.ค.', '69', 'เวลา', '13:00-16:30', 'น.']

    # ===== Processing ex_dur =====

    ex_dur_parts = exam_date_parts[6].split('-')            # ['13:00', '16:30']
    for i in range(len(ex_dur_parts)):
        ex_dur_parts[i] += ":00"                            # ['13:00:00', '16:30:00']

    ex_dur = " - ".join(ex_dur_parts)                       # '13:00:00 - 16:30:00'

    # ===== Processing ex_date =====

    day = exam_date_parts[2]                                # '16'
    month_str = exam_date_parts[3]                          # 'มี.ค.'
    buddhist_year_str = exam_date_parts[4]                  # '69'

    month = months[month_str]                               # '03'
    gregorian_year = int(buddhist_year_str) + 2500 - 543    # '2026'

    ex_date = f"{gregorian_year}-{month}-{day}"

    # ===== Processing ex_time =====

    ex_time = ex_dur[:2]                                    # '13'

    # ===== Processing ex_dt =====

    ex_dt = f"{ex_date} {ex_time}"                          # '2026-03-16 13'

    return ex_dur, ex_date, ex_time, ex_dt

df = convert_exam_report("16 บ่าย.xls")
# %%