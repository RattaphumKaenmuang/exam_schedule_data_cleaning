# %%
import pandas as pd

def convert_exam_report(file_path: str) -> pd.DataFrame:
    """
    อ่านไฟล์รายงานตารางสอบ (.xls) จาก file_path
    แล้วคืนค่าเป็น pandas DataFrame ตามรูปแบบที่กำหนด
    """
    ...
    df = pd.read_excel(file_path)
    return df