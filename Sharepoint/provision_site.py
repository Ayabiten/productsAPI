import os
import pandas as pd
from sharepoint_packages.auth.models import SharePointToken, CookieAuthToken, LocalBrowserAuthToken
from sharepoint_packages.api.base_client import SharePointClient, SharePointAPIError
from sharepoint_packages.api.models import ListPayload, FieldPayload, ViewPayload, ListItemPayload
from sharepoint_packages.api.lists import ListsAPI
from sharepoint_packages.api.list_views import ListViewsAPI
from sharepoint_packages.api.items import ItemsAPI
from sharepoint_packages.api.groups import GroupsAPI
from sharepoint_packages.api.roles import RolesAPI

def sanitize_bool(val) -> bool:
    if pd.isna(val):
        return False
    if str(val).strip().lower() in ['true', 'yes', '1']:
        return True
    return False

def provision_site():
    print("--- SharePoint Excel Provisioning Engine ---\n")

    # 1. Setup Auth and Client
    # Option A: Bearer Token
    # ACCESS_TOKEN = "eyJ0eX..." 
    # token = SharePointToken(access_token=ACCESS_TOKEN, token_type="Bearer")
    
    # Option B: FedAuth / rtFa Cookies (manual)
    # FED_AUTH = "77u/PD94b..."
    # RT_FA = "f4HjN..."
    # token = CookieAuthToken(fed_auth=FED_AUTH, rt_fa=RT_FA)

    # Option C: Extract Cookies automatically from local Chrome/Edge
    # Ensure you have pip install pywin32 cryptography
    # token = LocalBrowserAuthToken(domain="yourtenant.sharepoint.com", browser="chrome")

    # (Fallback default for the script to run)
    token = CookieAuthToken(fed_auth="manual", rt_fa="manual")

    SITE_URL = "https://yourtenant.sharepoint.com/sites/yoursite"
    client = SharePointClient(site_url=SITE_URL, auth_token=token)

    lists_api = ListsAPI(client)
    views_api = ListViewsAPI(client)
    items_api = ItemsAPI(client)
    groups_api = GroupsAPI(client)
    roles_api = RolesAPI(client)

    # 2. Read Excel Configuration
    template_path = "templates/sharepoint_config.xlsx"
    if not os.path.exists(template_path):
        print(f"[!] Error: Cannot find {template_path}. Please run generate_template.py first.")
        return

    print(f"[*] Reading configuration from {template_path}")
    df_lists = pd.read_excel(template_path, sheet_name="Lists")
    df_columns = pd.read_excel(template_path, sheet_name="Columns")
    df_views = pd.read_excel(template_path, sheet_name="Views")
    df_groups = pd.read_excel(template_path, sheet_name="Groups")
    df_data = pd.read_excel(template_path, sheet_name="DataImport")

    try:
        # --- Provision Groups ---
        print("\n[*] Provisioning Groups...")
        for _, row in df_groups.iterrows():
            group_name = str(row['GroupName'])
            desc = str(row['Description']) if pd.notna(row['Description']) else ""
            try:
                new_group = groups_api.create_group(group_name, desc)
                print(f"    Created Group: {group_name}")
                group_id = new_group['Id']
                
                # Try to assign role if defined
                role_name = row.get('RoleName')
                if pd.notna(role_name):
                    try:
                        role_def = roles_api.get_role_definition_by_name(str(role_name))
                        roles_api.add_role_assignment(group_id, role_def['Id'])
                        print(f"    Assigned Role '{role_name}' to Group '{group_name}'")
                    except SharePointAPIError as e:
                        print(f"    [!] Warning: Could not assign role '{role_name}'. It may not exist. Ensure you have created the custom permission level in Site Settings. Error: {e.status_code}")
            except SharePointAPIError as e:
                print(f"    [!] Failed to create group {group_name} (It might already exist).")

        # --- Provision Lists ---
        print("\n[*] Provisioning Lists...")
        for _, row in df_lists.iterrows():
            list_title = str(row['Title'])
            payload = ListPayload(
                title=list_title,
                description=str(row['Description']) if pd.notna(row['Description']) else "",
                base_template=int(row['BaseTemplate']) if pd.notna(row['BaseTemplate']) else 100,
                allow_content_types=sanitize_bool(row.get('AllowContentTypes'))
            )
            try:
                lists_api.create(payload)
                print(f"    Created List: {list_title}")
            except SharePointAPIError as e:
                print(f"    [!] Failed to create List {list_title}. Error: {e.status_code}")

        # --- Provision Columns ---
        print("\n[*] Provisioning Columns...")
        for _, row in df_columns.iterrows():
            list_title = str(row['ListTitle'])
            col_payload = FieldPayload(
                title=str(row['Title']),
                field_type_kind=int(row['FieldTypeKind']),
                required=sanitize_bool(row.get('Required')),
                read_only=sanitize_bool(row.get('ReadOnly'))
            )
            
            if pd.notna(row.get('Choices')):
                col_payload.choices = [c.strip() for c in str(row['Choices']).split(',')]
            if pd.notna(row.get('Formula')):
                col_payload.formula = str(row['Formula'])
            if pd.notna(row.get('LookupListId')):
                col_payload.lookup_list_id = str(row['LookupListId'])
            if pd.notna(row.get('LookupFieldName')):
                col_payload.lookup_field_name = str(row['LookupFieldName'])

            try:
                lists_api.create_field(list_title, col_payload)
                print(f"    Created Column '{row['Title']}' in '{list_title}'")
            except SharePointAPIError as e:
                print(f"    [!] Failed to create column '{row['Title']}'. Error: {e.status_code}")

        # --- Provision Views ---
        print("\n[*] Provisioning Views...")
        for _, row in df_views.iterrows():
            list_title = str(row['ListTitle'])
            view_payload = ViewPayload(
                title=str(row['ViewTitle']),
                personal_view=sanitize_bool(row.get('PersonalView')),
                row_limit=int(row['RowLimit']) if pd.notna(row['RowLimit']) else 30,
                view_query=str(row['ViewQuery']) if pd.notna(row['ViewQuery']) else "",
                view_fields=[f.strip() for f in str(row['ViewFields']).split(',')] if pd.notna(row['ViewFields']) else []
            )
            try:
                views_api.create_view(list_title, view_payload)
                print(f"    Created View '{row['ViewTitle']}' in '{list_title}'")
            except SharePointAPIError as e:
                print(f"    [!] Failed to create view '{row['ViewTitle']}'. Error: {e.status_code}")

        # --- Import Data ---
        print("\n[*] Importing Data...")
        for _, row in df_data.iterrows():
            list_title = str(row['ListTitle'])
            # Drop the ListTitle from the dictionary and drop nulls
            row_dict = row.drop('ListTitle').dropna().to_dict()
            
            # Note: SharePoint requires the specific List Item Type __metadata 
            # Format usually: SP.Data.<ListTitle>ListItem
            safe_title = list_title.replace(" ", "_x0020_")
            metadata_type = f"SP.Data.{safe_title}ListItem"
            
            item_payload = ListItemPayload(
                type=metadata_type,
                fields=row_dict
            )
            try:
                items_api.create_item(list_title, item_payload)
                print(f"    Imported row into '{list_title}'")
            except SharePointAPIError as e:
                print(f"    [!] Failed to import row into '{list_title}'. Error: {e.status_code}")

        print("\n[+] Provisioning complete!")

    except Exception as e:
        print(f"\n[!] Unexpected Script Error: {str(e)}")

if __name__ == "__main__":
    provision_site()
