#!/bin/bash
# 设置/取消系统代理
# 用法: source proxy.sh on   # 开启代理
#       source proxy.sh off  # 关闭代理

PROXY_HTTP="http://127.0.0.1:7890"
PROXY_SOCKS="socks5://127.0.0.1:7891"

if [ "$1" = "on" ]; then
    export http_proxy="$PROXY_HTTP"
    export https_proxy="$PROXY_HTTP"
    export HTTP_PROXY="$PROXY_HTTP"
    export HTTPS_PROXY="$PROXY_HTTP"
    export ALL_PROXY="$PROXY_SOCKS"
    export no_proxy="localhost,127.0.0.1,192.168.0.0/16"
    echo "✅ 代理已开启 (http://127.0.0.1:7890)"
elif [ "$1" = "off" ]; then
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
    echo "✅ 代理已关闭"
elif [ "$1" = "status" ]; then
    if [ -n "$http_proxy" ]; then
        echo "代理开启: $http_proxy"
    else
        echo "代理关闭"
    fi
else
    echo "用法: source proxy.sh {on|off|status}"
fi
