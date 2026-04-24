#!/usr/bin/env python
"""Django管理脚本"""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("无法导入Django，请确认已安装") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
