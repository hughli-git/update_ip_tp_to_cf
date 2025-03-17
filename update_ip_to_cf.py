from tplink import TPlink
from cloudflaredns import CloudflareDns
from check_duplicate import check_duplicate_script
import time
from datetime import datetime
import traceback
import secret_settings


def log(log_str):
    print(datetime.now(), log_str)


def main():
    # cloudflare 认证
    cf_obj = CloudflareDns(secret_settings.CF_KEY, secret_settings.CF_DOMAIN)
    # 路由器认证
    tp = TPlink(secret_settings.TP_HOST, secret_settings.TP_USER, secret_settings.TP_PWD)
    # 首次运行直接获取认证信息
    tp._get_auth_tokens_rsa()
    cached_ip = {}
    while True:
        time.sleep(secret_settings.PERIOD_UPDATE)
        try:
            ret = tp.get_wan_ip_list()
            log(f"get IP {ret}")
            # 认证过期, 可能是有用户通过web登录路由器
            # 1小时候再认证避免用户的web登录态失效
            if not ret:
                log("TPLink auth error, sleep 1h")
                time.sleep(secret_settings.PERIOD_AUTH)
                tp._get_auth_tokens_rsa()
                continue

            for key in ret:
                if key in cached_ip and cached_ip[key] == ret[key]:
                    continue
                cached_ip[key] = ret[key]
                log(f"start update CF {key} {secret_settings.DOMAIN_LIST[key]} {ret[key]}")
                update_result = cf_obj.update_dns_record(secret_settings.DOMAIN_LIST[key], ret[key])
                if not update_result['success']:
                    log(f"ERROR update {update_result}")
            log("finish update")
        except:
            log(traceback.format_exc())


if __name__ == "__main__":
    check_duplicate_script()
    while True:
        try:
            main()
        except:
            log(traceback.format_exc())
        time.sleep(secret_settings.PERIOD_UPDATE)
