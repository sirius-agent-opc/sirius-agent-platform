#!/bin/bash
# VPN 停止脚本
pkill -f mihomo 2>/dev/null && echo "✅ mihomo 已停止" || echo "mihomo 未运行"