import sys
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parent.parent / "语文AI教学智能体"
sys.path.insert(0, str(APP_DIR))

import config  # noqa: E402
from data.textbooks import (  # noqa: E402
    GRADE_LEVELS,
    TEACHING_STYLES,
    TEXTBOOKS,
    get_grades,
    get_textbooks,
)
from export import export_to_markdown, get_download_data  # noqa: E402
from mimo_client import MiMoClient, get_client, reset_client  # noqa: E402
from prompts import (  # noqa: E402
    get_analysis_prompt,
    get_homework_prompt,
    get_interaction_prompt,
    get_lesson_plan_prompt,
    get_reading_prompt,
    get_system_prompt,
    get_writing_prompt,
)


def test_curriculum_catalog_consistency():
    assert set(GRADE_LEVELS.keys()) == {"小学", "初中", "高中"}
    total_volumes = sum(len(vols) for vols in GRADE_LEVELS.values())
    assert total_volumes == 24
    for level, volumes in GRADE_LEVELS.items():
        assert get_grades(level) == volumes
        for vol in volumes:
            lessons = get_textbooks(vol)
            assert isinstance(lessons, list)
            assert len(lessons) > 0
            assert vol in TEXTBOOKS


def test_teaching_styles_and_prompts():
    assert len(TEACHING_STYLES) == 6
    sys_prompt = get_system_prompt("初中", "启发探究型")
    assert "初中" in sys_prompt
    assert "启发探究型" in sys_prompt

    assert "背影" in get_analysis_prompt("八年级上册", "背影")
    assert "背影" in get_lesson_plan_prompt("八年级上册", "背影", "启发探究型")
    assert "背影" in get_interaction_prompt("八年级上册", "背影")
    assert "背影" in get_homework_prompt("八年级上册", "背影")
    assert "散文" in get_reading_prompt("八年级上册", "散文")
    assert "背影" in get_writing_prompt("八年级上册", "背影")


def test_export_to_markdown():
    md = export_to_markdown("## 教学目标\n- 掌握重点词句", "八年级上册", "背影", "教案")
    assert "# 八年级上册《背影》教案" in md
    assert "掌握重点词句" in md


def test_get_download_data_markdown_and_docx():
    content = "# 一级标题\n## 二级标题\n- 列表项\n1. 编号项\n【教学重点】\n> 引用\n---"

    md_bytes, err, filename = get_download_data(content, "八年级上册", "背影", fmt="markdown", plan_type="教案")
    assert err is None
    assert filename == "八年级上册_背影_教案.md"
    assert "八年级上册《背影》教案".encode("utf-8") in md_bytes

    docx_bytes, err, filename = get_download_data(content, "八年级上册", "背影", fmt="docx", plan_type="教案")
    assert err is None
    assert filename == "八年级上册_背影_教案.docx"
    assert docx_bytes.startswith(b"PK\x03\x04")


def test_mimo_client_payload_and_runtime_config(monkeypatch):
    client = MiMoClient(api_key="k", base_url="http://localhost:9999", model="test-model")
    payload = client._prepare_payload(
        [
            {"role": "system", "content": "系统提示词"},
            {"role": "user", "content": "请解析《背影》"},
        ],
        temperature=0.0,
        max_tokens=256,
    )
    assert payload["model"] == "test-model"
    assert payload["temperature"] == 0.0
    assert payload["max_tokens"] == 256
    assert payload["system"] == "系统提示词"
    assert payload["messages"] == [{"role": "user", "content": "请解析《背影》"}]

    # Runtime config update reflected after reset_client()
    monkeypatch.setattr(config, "MIMO_MODEL", "updated-model")
    reset_client()
    reloaded = get_client()
    assert reloaded.model == "updated-model"
    reset_client()

    # Error handling returns consistent warning banner for both modes and test_connection
    class _FailingMessages:
        def create(self, **kwargs):
            raise RuntimeError("boom")

        def stream(self, **kwargs):
            raise RuntimeError("stream boom")

    client.client = SimpleNamespace(messages=_FailingMessages())
    ok, msg = client.test_connection()
    assert ok is False
    assert msg.startswith("⚠️")
    chunks = list(client.chat([{"role": "user", "content": "hi"}], stream=True))
    assert chunks == ["\n⚠️ API调用出错：stream boom"]
