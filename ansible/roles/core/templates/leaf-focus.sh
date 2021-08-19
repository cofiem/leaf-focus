function leafFocusDownload(){
  export LEAF_FOCUS_CONFIG_FILE="{{ app_conf_main_file }}"
  export SCRAPY_SETTINGS_MODULE="leaf_focus.components.download.settings"
  "{{ app_venv_dir }}/bin/python" "{{ app_source_dir }}/leaf_focus/run.py" --config-file "{{ app_conf_main_file }}" "$@"
}
