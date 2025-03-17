# 从TPLink路由器读取WAN IP并更新到CloudFlare DNS

# install

```
poetry install
```

# 文件

`tplink.py` 自己调试好的tplink路由器认证以及获取WLAN地址逻辑
`check_duplicate.py` 防止脚本重复执行
`cloudflaredns.py` CF更新DNS API
`update_ip_to_cf.py` 主体函数, 常驻进程
`secret_settings.py` 密码配置文件
