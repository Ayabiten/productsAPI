import os
from sharepoint_packages.auth.models import SharePointToken, CookieAuthToken, LocalBrowserAuthToken
from sharepoint_packages.api.base_client import SharePointClient, SharePointAPIError
from sharepoint_packages.api.models import ListItemPayload, FileUploadMetadata, ListPayload, ViewPayload, FieldPayload
from sharepoint_packages.api.lists import ListsAPI
from sharepoint_packages.api.list_views import ListViewsAPI
from sharepoint_packages.api.items import ItemsAPI
from sharepoint_packages.api.files import FilesAPI
from sharepoint_packages.api.groups import GroupsAPI
from sharepoint_packages.api.sites import SitesAPI

def main():
    print("--- SharePoint API Example Usage ---\n")

    # 1. Authentication
    # Option A: Replace with your actual token fetched via Azure AD (MSAL) or other auth flows
    # ACCESS_TOKEN = "eyJ0eX..." 
    # token = SharePointToken(access_token=ACCESS_TOKEN, token_type="Bearer")
    
    # Option B: Authentication using FedAuth and rtFa cookies from a browser session
    FED_AUTH = "77u/PD94b..."
    RT_FA = "f4HjN..."
    token = CookieAuthToken(fed_auth=FED_AUTH, rt_fa=RT_FA)

    SITE_URL = "https://yourtenant.sharepoint.com/sites/yoursite"
    
    # Initialize the core client
    client = SharePointClient(site_url=SITE_URL, auth_token=token)

    # Initialize all APIs
    lists_api = ListsAPI(client)
    views_api = ListViewsAPI(client)
    items_api = ItemsAPI(client)
    files_api = FilesAPI(client)
    groups_api = GroupsAPI(client)
    sites_api = SitesAPI(client)

    try:
        # ---------------------------------------------------------
        # SITES API
        # ---------------------------------------------------------
        print("[*] Sites & Web")
        site_props = sites_api.get_site_properties()
        web_props = sites_api.get_web_properties()
        print(f"    Connected to Web: {web_props.get('Title')}\n")

        # ---------------------------------------------------------
        # GROUPS API
        # ---------------------------------------------------------
        print("[*] Groups")
        groups = groups_api.get_site_groups()
        print(f"    Found {len(groups)} groups.")
        # Example of getting users in a group
        # users = groups_api.get_users_in_group('Site Members')
        print()

        # ---------------------------------------------------------
        # LISTS API
        # ---------------------------------------------------------
        print("[*] Lists - Create")
        list_payload = ListPayload(
            title="My Test List",
            description="A list created via Python SDK",
            base_template=100, # 100 = Custom List, 101 = Document Library
            allow_content_types=True
        )
        # Uncomment to test creation:
        # new_list = lists_api.create(list_payload)
        # list_id = new_list['Id']
        # print(f"    Created list with ID: {list_id}")

        print("[*] Lists - Get")
        # all_lists = lists_api.get_all()
        # my_list = lists_api.get_by_title("My Test List")
        print()

        print("[*] Lists - Create Column (Field)")
        # FieldTypeKind: 2 = Text, 6 = Choice, 7 = Lookup, 9 = Number, 17 = Calculated
        field_payload = FieldPayload(
            title="MyCustomChoiceColumn",
            field_type_kind=6, # Choice
            required=False,
            read_only=False,
            choices=["Option A", "Option B", "Option C"]
        )
        # Uncomment to create field:
        # new_field = lists_api.create_field("My Test List", field_payload)
        
        # Example of a Calculated Field (Read Only by nature):
        # calc_field_payload = FieldPayload(
        #     title="TotalPrice",
        #     field_type_kind=17, # Calculated
        #     formula="=[Quantity] * [UnitPrice]",
        #     read_only=True
        # )
        # lists_api.create_field("My Test List", calc_field_payload)

        # Example of a Lookup Field:
        # lookup_field_payload = FieldPayload(
        #     title="RelatedCustomer",
        #     field_type_kind=7, # Lookup
        #     lookup_list_id="{TARGET-LIST-GUID-HERE}",
        #     lookup_field_name="Title" # The column in the target list to display
        # )
        # lists_api.create_field("My Test List", lookup_field_payload)
        print()

        # ---------------------------------------------------------
        # ITEMS API (CRUD)
        # ---------------------------------------------------------
        print("[*] Items - Create")
        # Note: metadata_type (alias 'type') is required for list item creation in SP
        # It usually follows the format 'SP.Data.ListNameListItem'.
        item_payload = ListItemPayload(
            type="SP.Data.My_x0020_Test_x0020_ListListItem", 
            fields={
                "Title": "New Item 1",
                "CustomColumn": "Some Value"
            }
        )
        # Uncomment to create item:
        # created_item = items_api.create_item("My Test List", item_payload)
        # item_id = created_item['Id']

        print("[*] Items - Update")
        update_payload = ListItemPayload(
            type="SP.Data.My_x0020_Test_x0020_ListListItem",
            fields={
                "Title": "Updated Title"
            }
        )
        # items_api.update_item("My Test List", item_id, update_payload)

        print("[*] Items - Get & Filter")
        # Example OData Filter to get specific items
        # filtered_items = items_api.get_items("My Test List", select="Id,Title", filter_query="Title eq 'Updated Title'")
        print()

        # ---------------------------------------------------------
        # LIST VIEWS API
        # ---------------------------------------------------------
        print("[*] Views - Create")
        view_payload = ViewPayload(
            title="My Custom View",
            personal_view=False,
            row_limit=50,
            # CAML Query to filter the view (e.g., Only items where Title is not null)
            view_query="<Where><IsNotNull><FieldRef Name='Title'/></IsNotNull></Where>",
            # The columns that will be visible in this view
            view_fields=["LinkTitle", "CustomColumn"]
        )
        # Uncomment to create view:
        # new_view = views_api.create_view("My Test List", view_payload)

        print("[*] Views - Update")
        # Note: updating a view takes a raw dictionary. Must include __metadata type.
        view_updates = {
            "__metadata": { "type": "SP.View" },
            "RowLimit": 100
        }
        # view_guid = new_view['Id']
        # views_api.update_view("My Test List", view_guid, view_updates)
        print()

        # ---------------------------------------------------------
        # FILES API
        # ---------------------------------------------------------
        print("[*] Files - Upload")
        file_meta = FileUploadMetadata(
            name="test_document.txt",
            content=b"Hello from Python!",
            overwrite=True
        )
        folder_url = "/sites/yoursite/Shared Documents"
        # Uncomment to upload file:
        # uploaded_file = files_api.upload_file(folder_url, file_meta)
        
        print("[*] Files - Download")
        file_url = "/sites/yoursite/Shared Documents/test_document.txt"
        # file_content_bytes = files_api.download_file(file_url)

    except SharePointAPIError as e:
        print(f"\n[!] SharePoint API Error Encountered!")
        print(f"Message: {str(e)}")
        if e.status_code:
            print(f"Status Code: {e.status_code}")
        if e.response_text:
            print(f"Response Body: {e.response_text}")
    except Exception as e:
        print(f"\n[!] Unexpected Error: {str(e)}")

if __name__ == "__main__":
    main()
