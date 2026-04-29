import os
from servicenow_packages import (
    BasicAuthModel, 
    ServiceNowClient, 
    TableAPI, 
    AttachmentAPI, 
    AggregateAPI,
    CSMAPI,
    CMDBAPI,
    AssetAPI,
    AgentAPI
)

def main():
    # 1. Initialize Authentication and Client
    auth = BasicAuthModel(
        username=os.getenv("SN_USERNAME", "admin"),
        password=os.getenv("SN_PASSWORD", "password")
    )
    
    # Use your real ServiceNow developer instance URL
    client = ServiceNowClient(
        instance_url="https://dev12345.service-now.com",
        auth=auth
    )
    
    # Initialize our API wrappers
    table_api = TableAPI(client)
    attachment_api = AttachmentAPI(client)
    aggregate_api = AggregateAPI(client)
    csm_api = CSMAPI(client)
    cmdb_api = CMDBAPI(client)
    asset_api = AssetAPI(client)
    agent_api = AgentAPI(client)
    
    try:
        # --- SCENARIO 1: ITSM (Incident Management) ---
        print("\n=== SCENARIO 1: Incident Management ===")
        # Create a new High Priority Incident ticket
        incident_data = {
            "short_description": "Database server CPU at 99%",
            "description": "The production database server is experiencing unusually high CPU usage.",
            "urgency": "1", # 1 = High
            "impact": "1",  # 1 = High
            "category": "database",
            "caller_id": "admin"
        }
        print("Creating Incident...")
        new_inc = table_api.create_record("incident", incident_data)
        inc_sys_id = new_inc.get("sys_id")
        inc_number = new_inc.get("number")
        print(f"Created Incident: {inc_number} (sys_id: {inc_sys_id})")
        
        # Add a Work Note to the incident
        print(f"Adding Work Note to {inc_number}...")
        table_api.update_record("incident", inc_sys_id, {
            "work_notes": "Investigating the CPU spikes. Looks like a rogue query."
        })
        
        # --- SCENARIO 2: CSM (Customer Service Management) ---
        print("\n=== SCENARIO 2: CSM (Accounts & Cases) ===")
        print("Fetching Accounts...")
        accounts = csm_api.get_accounts(limit=2)
        for acc in accounts:
            print(f"- Account: {acc.get('name')} (sys_id: {acc.get('sys_id')})")
        
        print("Creating a new Case...")
        case_data = {
            "short_description": "Internet connection issue for Customer",
            "priority": "2",
            "account": accounts[0].get('sys_id') if accounts else None
        }
        new_case = csm_api.create_case(case_data)
        print(f"Created Case: {new_case.get('number')} (sys_id: {new_case.get('sys_id')})")

        # --- SCENARIO 3: CMDB Instance API ---
        print("\n=== SCENARIO 3: CMDB Instance API ===")
        print("Fetching Linux Servers from CMDB...")
        servers = cmdb_api.get_ci_instances(class_name="cmdb_ci_linux_server", limit=2)
        for server in servers:
            print(f"- Server: {server.get('name')} (sys_id: {server.get('sys_id')})")

        # --- SCENARIO 4: Asset Management ---
        print("\n=== SCENARIO 4: Asset Management ===")
        print("Fetching Assets from alm_asset...")
        assets = asset_api.get_assets(limit=2)
        for asset in assets:
            print(f"- Asset Tag: {asset.get('asset_tag')} (Serial: {asset.get('serial_number')})")

        # --- SCENARIO 5: Agent Client Collector ---
        print("\n=== SCENARIO 5: Agent Client Collector ===")
        print("Fetching Agents...")
        agents = agent_api.get_agents(limit=2)
        for agent in agents:
            print(f"- Agent Name: {agent.get('name')} (ID: {agent.get('agent_id')})")
            status = agent_api.get_agent_status(agent.get('agent_id'))
            print(f"  Status: {status.get('status')}")

        # --- SCENARIO 6: Aggregate API (Reporting) ---
        print("\n=== SCENARIO 6: Aggregate API (Reporting) ===")
        # Count how many incidents are Active and High Priority
        print("Counting Active High Priority Incidents...")
        stats = aggregate_api.get_stats(
            table_name="incident",
            query="active=true^priority=1",
            count=True
        )
        count = stats.get('stats', {}).get('count', '0')
        print(f"Total Active High Priority Incidents: {count}")

        # --- CLEANUP ---
        print("\n=== CLEANUP ===")
        print(f"Deleting Incident {inc_number}...")
        table_api.delete_record("incident", inc_sys_id)
        if new_case.get('sys_id'):
            print(f"Deleting Case {new_case.get('number')}...")
            table_api.delete_record("sn_customerservice_case", new_case.get('sys_id'))
        print("Cleanup complete!")
        
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    main()

