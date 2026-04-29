import os
import pandas as pd

def generate_template():
    output_dir = "templates"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = os.path.join(output_dir, "sharepoint_config.xlsx")

    # Define DataFrames with columns and empty data (except for example rows)
    
    # 1. Lists
    df_lists = pd.DataFrame([
        {"Title": "ExampleList", "Description": "A test list", "BaseTemplate": 100, "AllowContentTypes": "TRUE"}
    ])
    
    # 2. Columns
    # FieldTypeKind: 2=Text, 3=Note, 4=DateTime, 6=Choice, 7=Lookup, 8=Boolean, 9=Number, 17=Calculated
    df_columns = pd.DataFrame([
        {"ListTitle": "ExampleList", "Title": "Description", "FieldTypeKind": 3, "Required": "FALSE", "ReadOnly": "FALSE", "Choices": "", "Formula": "", "LookupListId": "", "LookupFieldName": ""},
        {"ListTitle": "ExampleList", "Title": "Category", "FieldTypeKind": 6, "Required": "TRUE", "ReadOnly": "FALSE", "Choices": "Hardware,Software,Service", "Formula": "", "LookupListId": "", "LookupFieldName": ""},
        {"ListTitle": "ExampleList", "Title": "Price", "FieldTypeKind": 9, "Required": "FALSE", "ReadOnly": "FALSE", "Choices": "", "Formula": "", "LookupListId": "", "LookupFieldName": ""}
    ])
    
    # 3. Views
    df_views = pd.DataFrame([
        {"ListTitle": "ExampleList", "ViewTitle": "Hardware View", "PersonalView": "FALSE", "RowLimit": 30, "ViewQuery": "<Where><Eq><FieldRef Name='Category'/><Value Type='Choice'>Hardware</Value></Eq></Where>", "ViewFields": "LinkTitle,Description,Category,Price"}
    ])
    
    # 4. Groups
    df_groups = pd.DataFrame([
        {"GroupName": "List Editors", "Description": "Can edit items but not delete or create lists.", "RoleName": "Contribute Without Delete"}
    ])
    
    # 5. DataImport
    df_data = pd.DataFrame([
        {"ListTitle": "ExampleList", "Title": "Laptop", "Description": "Dell XPS 15", "Category": "Hardware", "Price": 1500},
        {"ListTitle": "ExampleList", "Title": "Office 365", "Description": "Annual Subscription", "Category": "Software", "Price": 100}
    ])

    # Write to Excel
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df_lists.to_excel(writer, sheet_name="Lists", index=False)
        df_columns.to_excel(writer, sheet_name="Columns", index=False)
        df_views.to_excel(writer, sheet_name="Views", index=False)
        df_groups.to_excel(writer, sheet_name="Groups", index=False)
        df_data.to_excel(writer, sheet_name="DataImport", index=False)

    print(f"[+] Successfully generated template at {file_path}")

if __name__ == "__main__":
    generate_template()
