import pandas as pd
from pathlib import Path
from datetime import datetime

def log_run(row_dict: dict, excel_path: Path = Path("data/experiment_results.xlsx"), sheet_name: str = "Runs") -> None:
    """
    Logs a dictionary of data as a new row to an Excel workbook.

    Creates the workbook if it does not exist; otherwise appends
    below the last populated row. Ensures header is written for new files
    or new/empty sheets.
    """
    df_new_row = pd.DataFrame([row_dict])

    if not excel_path.exists():
        # File doesn't exist, create it with header
        df_new_row.to_excel(excel_path, sheet_name=sheet_name, index=False, header=True)
        print(f"Created new Excel file and logged data to {excel_path}")
    else:
        # File exists, use ExcelWriter to append
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                workbook = writer.book
                if sheet_name not in workbook.sheetnames:
                    # Sheet is new in this workbook, write with header
                    df_new_row.to_excel(writer, sheet_name=sheet_name, index=False, header=True, startrow=0)
                    print(f"Created new sheet '{sheet_name}' and logged data to {excel_path}")
                else:
                    # Sheet exists, check if it's empty
                    sheet = workbook[sheet_name]
                    if sheet.max_row == 0:
                        # Sheet is empty, write with header at the beginning
                        df_new_row.to_excel(writer, sheet_name=sheet_name, index=False, header=True, startrow=0)
                    else:
                        # Sheet has content, append without header at the end
                        df_new_row.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=sheet.max_row)
                    print(f"Appended data to existing sheet '{sheet_name}' in {excel_path}")
        except Exception as e:
            print(f"An error occurred during Excel append: {e}. Attempting to overwrite/create the file with the current row as a fallback.")
            # Fallback: Try to save the new row, potentially overwriting or creating the file.
            try:
                df_new_row.to_excel(excel_path, sheet_name=sheet_name, index=False, header=True)
                print(f"Fallback: Saved data by overwriting/creating {excel_path}")
            except Exception as ex_fallback:
                print(f"Fallback save also failed: {ex_fallback}")

if __name__ == '__main__':
    # Example Usage
    mock_data_1 = {
        "timestamp": datetime.now(),
        "llm_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "system_prompt": "You are a helpful AI assistant.",
        "schema_provided": True,
        "query_complexity": "medium",
        "question": "What is the capital of France?",
        "generated_sql": "SELECT capital FROM countries WHERE name = 'France'",
        "sql_execution_result": "Paris",
        "answer": "The capital of France is Paris.",
        "run_id": 1
    }
    # log_run(mock_data_1) # Example call

    mock_data_2 = {
        "timestamp": datetime.now(),
        "llm_name": "gpt-4",
        "temperature": 0.5,
        "system_prompt": "You are an expert SQL writer.",
        "schema_provided": False,
        "query_complexity": "easy",
        "question": "How many users are there?",
        "generated_sql": "SELECT COUNT(*) FROM users",
        "sql_execution_result": "1500",
        "answer": "There are 1500 users.",
        "run_id": 2
    }
    # log_run(mock_data_2) # Example call
    # print(f"Example: Logged data to {Path('experiment_results.xlsx').resolve()}")
    pass # Keep __main__ clean for module usage

