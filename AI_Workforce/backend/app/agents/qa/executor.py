def execute_existing_tests(client, workspace: str) -> dict:
    """Run the Developer Agent's existing approved test command."""
    result = client.run_command(workspace, "test")

    return {
        "command": result["command"],
        "ok": result["ok"],
        "exit_code": result["exit_code"],
        "output": result["output"],
    }