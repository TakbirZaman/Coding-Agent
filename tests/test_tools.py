from ai_coding_agent import tools


def test_sandbox_blocks_escape(tmp_path):
    ws = tmp_path
    try:
        tools.read_file(ws, "../../secret.txt")
        assert False, "should block"
    except ValueError:
        pass

def test_write_read_roundtrip(tmp_path):
    tools.write_file(tmp_path, "a/b.txt", "hello")
    assert tools.read_file(tmp_path, "a/b.txt") == "hello"

def test_blocked_command(tmp_path):
    try:
        tools.run_shell(tmp_path, "rm -rf /")
        assert False
    except ValueError:
        pass
