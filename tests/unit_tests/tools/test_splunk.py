import pytest

from hackerbot.tools import SplunkTool, SplunkToolConfig


def test_splunk_result_table_formatting_csv(set_default_llm_url):
    test_data = [
        '"src_ip",count\n',
        '"10.10.10.10",1\n',
        '"10.10.10.10",2\n',
        '"10.10.10.10",3\n',
        '"10.10.10.10",4\n',
        '"10.10.10.10",5\n',
        '"10.10.10.10",6\n',
        '"10.10.10.10",7\n',
        '"10.10.10.10",8\n',
        '"10.10.10.10",9\n',
        '"10.10.10.10",10\n',
    ]

    splunk_conf = SplunkToolConfig(
        splunk_host="doesnt matter",
        splunk_port="1234",
        splunk_user="admin",
        splunk_pass="admin",
        use_static_env_map=True,
    )

    splunk = SplunkTool(splunk_conf)

    table = splunk.format_splunk_results_as_table(test_data, results_mode="csv")

    assert ['src_ip', 'count'] == table.field_names, "Expected table field names to be 'src_ip' and 'count'"

    assert len(table.rows) == len(test_data) - 1, f"Expected table rows to be exactly '{len(test_data) - 1}'"

def test_splunk_result_table_formatting_json(set_default_llm_url):
    test_data = [
        { "src_ip" : "10.10.10.10", "count" : "1" },
        { "src_ip" : "10.10.10.10", "count" : "2" },
        { "src_ip" : "10.10.10.10", "count" : "3" },
        { "src_ip" : "10.10.10.10", "count" : "4" },
        { "src_ip" : "10.10.10.10", "count" : "5" },
        { "src_ip" : "10.10.10.10", "count" : "6" },
        { "src_ip" : "10.10.10.10", "count" : "7" },
        { "src_ip" : "10.10.10.10", "count" : "8" },
        { "src_ip" : "10.10.10.10", "count" : "9" },
        { "src_ip" : "10.10.10.10", "count" : "10" },
    ]

    splunk_conf = SplunkToolConfig(
        splunk_host="doesnt matter",
        splunk_port="1234",
        splunk_user="admin",
        splunk_pass="admin",
        use_static_env_map=True,
    )

    splunk = SplunkTool(splunk_conf)

    table = splunk.format_splunk_results_as_table(test_data, results_mode="json")

    assert ['src_ip', 'count'] == table.field_names, "Expected table field names to be 'src_ip' and 'count'"

    assert len(table.rows) == len(test_data), f"Expected table rows to be exactly '{len(test_data)}'"

def test_splunk_result_table_formatting__error_invalid_results_mode(set_default_llm_url):
    test_data = [
        { "src_ip" : "10.10.10.10", "count" : "1" },
    ]

    splunk_conf = SplunkToolConfig(
        splunk_host="doesnt matter",
        splunk_port="1234",
        splunk_user="admin",
        splunk_pass="admin",
        use_static_env_map=True,
    )

    splunk = SplunkTool(splunk_conf)

    with pytest.raises(ValueError):
        splunk.format_splunk_results_as_table(test_data, results_mode="non-existent-mode")

def test_splunk_result_table_formatting_csv__error_not_list(set_default_llm_url):

    test_data = {
        "test" : [
            '"src_ip",count\n',
            '"10.10.10.10",1\n',
        ],
    }

    splunk_conf = SplunkToolConfig(
        splunk_host="doesnt matter",
        splunk_port="1234",
        splunk_user="admin",
        splunk_pass="admin",
        use_static_env_map=True,
    )

    splunk = SplunkTool(splunk_conf)

    with pytest.raises(TypeError):
        splunk.format_splunk_results_as_table(test_data, results_mode="csv")

def test_splunk_result_table_formatting_csv__error_type_list_item(set_default_llm_url):

    test_data = [
        '"src_ip",count\n',
        '"10.10.10.10",1\n',
        {}
    ]

    splunk_conf = SplunkToolConfig(
        splunk_host="doesnt matter",
        splunk_port="1234",
        splunk_user="admin",
        splunk_pass="admin",
        use_static_env_map=True,
    )

    splunk = SplunkTool(splunk_conf)

    with pytest.raises(TypeError):
        splunk.format_splunk_results_as_table(test_data, results_mode="csv")

def test_splunk_result_table_formatting_json__error_not_list(set_default_llm_url):

    test_data = {
        "test" : [
            '"src_ip",count\n',
            '"10.10.10.10",1\n',
        ],
    }

    splunk_conf = SplunkToolConfig(
        splunk_host="doesnt matter",
        splunk_port="1234",
        splunk_user="admin",
        splunk_pass="admin",
        use_static_env_map=True,
    )

    splunk = SplunkTool(splunk_conf)

    with pytest.raises(TypeError):
        splunk.format_splunk_results_as_table(test_data, results_mode="json")

def test_splunk_result_table_formatting_json__error_type_list_item(set_default_llm_url):

    test_data = [
        '"src_ip",count\n',
        '"10.10.10.10",1\n',
        {}
    ]

    splunk_conf = SplunkToolConfig(
        splunk_host="doesnt matter",
        splunk_port="1234",
        splunk_user="admin",
        splunk_pass="admin",
        use_static_env_map=True,
    )

    splunk = SplunkTool(splunk_conf)

    with pytest.raises(TypeError):
        splunk.format_splunk_results_as_table(test_data, results_mode="json")

def test_splunk_result_table_formatting_json_empty_data(set_default_llm_url):

    test_data = []

    splunk_conf = SplunkToolConfig(
        splunk_host="doesnt matter",
        splunk_port="1234",
        splunk_user="admin",
        splunk_pass="admin",
        use_static_env_map=True,
    )

    splunk = SplunkTool(splunk_conf)

    table = splunk.format_splunk_results_as_table(test_data, results_mode="json")

    assert table.field_names == [], "Expected table field names to be empty"
    assert table.rows == [], "Expected table rows to be empty"

def test_splunk_result_table_formatting_csv_empty_data(set_default_llm_url):

    test_data = []

    splunk_conf = SplunkToolConfig(
        splunk_host="doesnt matter",
        splunk_port="1234",
        splunk_user="admin",
        splunk_pass="admin",
        use_static_env_map=True,
    )

    splunk = SplunkTool(splunk_conf)

    table = splunk.format_splunk_results_as_table(test_data, results_mode="csv")

    assert table.field_names == [], "Expected table field names to be empty"
    assert table.rows == [], "Expected table rows to be empty"
