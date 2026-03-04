"""Post-workflow hook for Obsidian vault sync.

Usage (in any workflow's run.py, after BigBrain check):

    from lib.obsidian.hooks import post_workflow_sync
    post_workflow_sync(db)
"""

from config import OBSIDIAN_VAULT_PATH, OBSIDIAN_SYNC_SCOPE, OBSIDIAN_SYNC_SINCE_HOURS


def post_workflow_sync(db):
    """Sync latest workflow data to the Obsidian vault. Non-fatal on error."""
    try:
        from lib.obsidian.sync_tool import ObsidianSyncTool

        tool = ObsidianSyncTool(vault_path=OBSIDIAN_VAULT_PATH)
        result = tool.execute(
            db_client=db,
            sync_scope=OBSIDIAN_SYNC_SCOPE,
            since_hours=OBSIDIAN_SYNC_SINCE_HOURS,
        )
        if result["success"]:
            stats = result["data"]
            print(
                f"    Obsidian: synced {stats['workflows_synced']} workflows, "
                f"{stats['executions_synced']} executions, "
                f"{stats['proposals_synced']} proposals"
            )
        else:
            print(f"    Obsidian sync warning: {result['error']}")
    except Exception as e:
        print(f"    Obsidian sync skipped: {e}")
