from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
import requests
import re
import json
import time
import codecs
import math
from struct import unpack


class TPlink:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.stok = ""
        self.sysauth = ""
        self.password_rsa_public_key = []

    def _get_auth_tokens_rsa(self):
        print("Getting public RSA key")
        referer = "http://{}/webpages/login.html".format(self.host)
        url = "http://{}/cgi-bin/luci/;stok=/login".format(self.host)
        response = requests.post(
            url,
            params={"form": "login"},
            data={"data": json.dumps({"method": "get"})},
            headers={"Referer": referer},
            timeout=4,
        )
        print(response.json())
        try:
            self.password_rsa_public_key = response.json().get("result").get("password")
        except (ValueError, KeyError, AttributeError) as _:
            print("Couldn't fetch password RSA keys! Response was: %s", response.text)
            return False
        # Create MD5 hash of username concatenated with password
        rsa_modulus_n = bytes_to_long(bytes.fromhex(self.password_rsa_public_key[0]))
        rsa_public_exp = bytes_to_long(bytes.fromhex(self.password_rsa_public_key[1]))

        public_key = RSA.construct((rsa_modulus_n, rsa_public_exp))
        
        message = self.password.encode("utf-8")
        # 加密长度
        k = public_key.size_in_bytes()
        # 将ASCII码转换为int
        em_int = 0
        for i in message:
            em_int = (em_int << 8) + i
        # 补齐长度
        em_int = em_int << (8 * (k - len(message)))
        # RSA 算法
        m_int = public_key._encrypt(em_int)
        # 转换为bytes
        password_encrypted = long_to_bytes(m_int, k)

        password_hex = codecs.encode(password_encrypted, "hex").decode("utf-8")

        auth_data = json.dumps(
            {
                "params": {
                    "username": self.username,
                    "password": password_hex,
                },
                "method": "login",
            }
        )
        print("Retrieving auth tokens...")
        referer = "http://{}/webpages/index.html".format(self.host)
        url = "http://{}/cgi-bin/luci/;stok=/login".format(self.host)
        print(auth_data)
        response = requests.post(
            url,
            params={"form": "login"},
            data={"data": auth_data},
            headers={
                "Referer": referer,
            },
        )
        try:
            result_json = response.json()
            self.stok = result_json["result"]["stok"]
            print("get stok =", self.stok)
            regex_result = re.search("sysauth=(.*);", response.headers["set-cookie"])
            self.sysauth = regex_result.group(1)
            print("get sysauth =", self.sysauth)
            return True
        except (ValueError, KeyError, AttributeError) as e:
            print(e)
            print("Couldn't fetch auth tokens! Response was %d: %s" % (response.status_code, response.text))
            return False

    def get_wan_ip_list(self):
        # 若无认证 - 认证
        # 若有认证 - 测试认证是否有效
        # 若认证失效 - 等一小时再重新认证
        # 若认证有效 - 继续
        referer = "http://{}/webpages/index.html".format(self.host)
        url = f"http://{self.host}/cgi-bin/luci/;stok={self.stok}/admin/system_state"
        print(url)
        response = requests.post(
            url,
            params={"form": "system_state"},
            data={"data": json.dumps({"method": "get"})},
            headers={
                "Referer": referer,
            },
            cookies={"sysauth": self.sysauth},
        )
        ret_data = response.json()
        error_code = int(ret_data["error_code"])
        if error_code == 704:
            print("Auth error")
        elif error_code == 0:
            print(ret_data)
            ret = {}
            for one_port in response.json()["result"][0]["normal"]:
                if one_port.get("t_name") in ("WAN1", "WAN2"):
                    ret[one_port["t_name"]] = one_port["ipaddr"]
            return ret
        else:
            print(error_code, ret_data)


if __name__ == '__main__':
    tp = TPlink("192.168.60.1", "admin", "admin_pass")
    tp._get_auth_tokens_rsa()
    print(tp.get_wan_ip_list())
