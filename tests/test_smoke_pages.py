"""
tests/test_smoke_pages.py
==========================
Smoke tests that run the main app.py and all feature pages.
This ensures every page loads and executes its top-level Streamlit code
without syntax or runtime exceptions under a fully mocked Streamlit environment.
"""
import sys
import os
import pytest
from unittest import mock
import pandas as pd
import streamlit as st

# Define custom exceptions for mocked Streamlit flow controls
class MockRerunException(Exception):
    pass

class MockStopException(Exception):
    pass

class MockSessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

@pytest.fixture
def mock_streamlit(monkeypatch):
    """
    Sets up mocked functions on the real streamlit module to intercept
    all UI and control calls during smoke imports.
    """
    # Create session state and secrets mocks
    session_state_mock = MockSessionState()
    secrets_mock = {"GROQ_API_KEY": "gsk_mock_api_key_for_smoke_tests_valid_length"}

    # Mock rerun/stop exceptions to control flow
    monkeypatch.setattr(st, "rerun", mock.MagicMock(side_effect=MockRerunException("Rerun triggered")))
    monkeypatch.setattr(st, "stop", mock.MagicMock(side_effect=MockStopException("Stop triggered")))

    # Unpacking helpers for columns and tabs
    def mock_columns(*args, **kwargs):
        if args:
            spec = args[0]
        else:
            spec = kwargs.get("spec", 1)
        if isinstance(spec, int):
            return [mock.MagicMock() for _ in range(spec)]
        try:
            return [mock.MagicMock() for _ in range(len(spec))]
        except Exception:
            return [mock.MagicMock()]

    def mock_tabs(*args, **kwargs):
        if args:
            tabs = args[0]
        else:
            tabs = kwargs.get("tabs", [])
        try:
            return [mock.MagicMock() for _ in range(len(tabs))]
        except Exception:
            return [mock.MagicMock()]

    monkeypatch.setattr(st, "columns", mock_columns)
    monkeypatch.setattr(st, "tabs", mock_tabs)

    # Input elements mocks returning type-correct default values
    def mock_selectbox(*args, **kwargs):
        options = kwargs.get("options")
        if options is None and len(args) > 1:
            options = args[1]
        index = kwargs.get("index", 0)
        if index == 0 and len(args) > 2:
            index = args[2]
        if options:
            try:
                return options[index]
            except Exception:
                return options[0]
        return None

    def mock_multiselect(*args, **kwargs):
        default = kwargs.get("default")
        if default is None and len(args) > 2:
            default = args[2]
        if default is not None:
            return default
        return []

    def mock_slider(*args, **kwargs):
        value = kwargs.get("value")
        if value is None and len(args) > 3:
            value = args[3]
        if value is not None:
            return value
        min_value = kwargs.get("min_value")
        if min_value is None and len(args) > 1:
            min_value = args[1]
        if min_value is not None:
            return min_value
        return 0

    def mock_select_slider(*args, **kwargs):
        value = kwargs.get("value")
        if value is None and len(args) > 2:
            value = args[2]
        if value is not None:
            return value
        options = kwargs.get("options")
        if options is None and len(args) > 1:
            options = args[1]
        if options:
            return options[0]
        return None

    def mock_text_input(*args, **kwargs):
        value = kwargs.get("value", "")
        if value == "" and len(args) > 1:
            value = args[1]
        return value

    def mock_text_area(*args, **kwargs):
        value = kwargs.get("value", "")
        if value == "" and len(args) > 1:
            value = args[1]
        return value

    def mock_number_input(*args, **kwargs):
        value = kwargs.get("value", 0)
        if value == 0 and len(args) > 2:
            value = args[2]
        return value

    def mock_date_input(*args, **kwargs):
        value = kwargs.get("value")
        if value is None and len(args) > 1:
            value = args[1]
        return value

    def mock_time_input(*args, **kwargs):
        value = kwargs.get("value")
        if value is None and len(args) > 1:
            value = args[1]
        return value

    # Assign functions to st
    monkeypatch.setattr(st, "selectbox", mock_selectbox)
    monkeypatch.setattr(st, "multiselect", mock_multiselect)
    monkeypatch.setattr(st, "slider", mock_slider)
    monkeypatch.setattr(st, "select_slider", mock_select_slider)
    monkeypatch.setattr(st, "text_input", mock_text_input)
    monkeypatch.setattr(st, "text_area", mock_text_area)
    monkeypatch.setattr(st, "number_input", mock_number_input)
    monkeypatch.setattr(st, "date_input", mock_date_input)
    monkeypatch.setattr(st, "time_input", mock_time_input)

    # Assign to st.sidebar
    monkeypatch.setattr(st.sidebar, "selectbox", mock_selectbox)
    monkeypatch.setattr(st.sidebar, "multiselect", mock_multiselect)
    monkeypatch.setattr(st.sidebar, "slider", mock_slider)
    monkeypatch.setattr(st.sidebar, "select_slider", mock_select_slider)

    # Simple mock elements returning False or doing nothing
    monkeypatch.setattr(st, "button", mock.MagicMock(return_value=False))
    monkeypatch.setattr(st.sidebar, "button", mock.MagicMock(return_value=False))
    monkeypatch.setattr(st, "chat_input", mock.MagicMock(return_value=None))

    # Decorator/visual functions
    monkeypatch.setattr(st, "set_page_config", mock.MagicMock())
    monkeypatch.setattr(st, "markdown", mock.MagicMock())
    monkeypatch.setattr(st, "error", mock.MagicMock())
    monkeypatch.setattr(st, "warning", mock.MagicMock())
    monkeypatch.setattr(st, "success", mock.MagicMock())
    monkeypatch.setattr(st, "info", mock.MagicMock())
    monkeypatch.setattr(st, "caption", mock.MagicMock())
    monkeypatch.setattr(st, "plotly_chart", mock.MagicMock())
    monkeypatch.setattr(st, "download_button", mock.MagicMock())
    monkeypatch.setattr(st, "dataframe", mock.MagicMock())
    monkeypatch.setattr(st, "subheader", mock.MagicMock())
    monkeypatch.setattr(st, "metric", mock.MagicMock())

    monkeypatch.setattr(st.sidebar, "markdown", mock.MagicMock())
    monkeypatch.setattr(st.sidebar, "caption", mock.MagicMock())

    # Context managers
    class DummyContextManager:
        def __enter__(self):
            return mock.MagicMock()
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(st, "spinner", lambda *a, **kw: DummyContextManager())
    monkeypatch.setattr(st, "expander", lambda *a, **kw: DummyContextManager())
    monkeypatch.setattr(st, "chat_message", lambda *a, **kw: DummyContextManager())

    # Session State and Secrets
    monkeypatch.setattr(st, "session_state", session_state_mock)
    monkeypatch.setattr(st, "secrets", secrets_mock)
    
    return st


def _run_page_file(filepath):
    """Executes the Python file inside a clean namespace."""
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    # Run with custom namespace
    namespace = {
        "__file__": filepath,
        "__name__": "__main__",
    }
    
    try:
        exec(code, namespace)
    except (MockRerunException, MockStopException):
        # Triggering rerun or stop means the code successfully executed up to that flow control point
        pass


# ── Smoke Test Suite ──────────────────────────────────────────────────────────

PAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "pages")
APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app.py")

# Discovered pages dynamically to stay maintainable
def get_all_page_paths():
    paths = [APP_PATH]
    if os.path.exists(PAGES_DIR):
        for name in sorted(os.listdir(PAGES_DIR)):
            if name.endswith(".py"):
                paths.append(os.path.join(PAGES_DIR, name))
    return paths

@pytest.mark.parametrize("filepath", get_all_page_paths())
def test_page_loads_without_exception(filepath, mock_streamlit):
    """Verifies that the given streamlit page runs top-to-bottom without throwing exceptions."""
    # Ensure fresh session state for each page execution
    mock_streamlit.session_state.clear()
    _run_page_file(filepath)
