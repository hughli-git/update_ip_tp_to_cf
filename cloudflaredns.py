import requests
import json


class CloudflareDns:
    def __init__(self, api_token, zone_name):
        self.api_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.zone_id = self.get_zone_id(zone_name)

    def get_zone_id(self, domain):
        url = f"{self.api_url}/zones"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        zones = response.json()["result"]
        for zone in zones:
            if zone["name"] == domain:
                return zone["id"]
        raise ValueError("None zone id")

    # 获取 DNS 记录 ID
    def get_dns_record_id(self, record_name):
        url = f"{self.api_url}/zones/{self.zone_id}/dns_records"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        dns_records = response.json()["result"]
        for record in dns_records:
            if record["name"] == record_name:
                return record["id"]
        raise ValueError("None record_name")

    # 更新 DNS 记录
    def update_dns_record(self, record_name, new_ip, dns_type="A", ttl=1, proxied=False):
        record_id = self.get_dns_record_id(record_name)
        url = f"{self.api_url}/zones/{self.zone_id}/dns_records/{record_id}"
        data = {
            "type": dns_type,
            "name": record_name,
            "content": new_ip,
            "ttl": ttl,  # 自动 TTL
            "proxied": proxied  # 是否通过 Cloudflare 代理
        }
        response = requests.put(url, headers=self.headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    obj = CloudflareDns("000000000oQxCG3hBCuT4DPr9_Pqf3CVKL7170000", "passdomain.cn")
    ret = obj.update_dns_record("sub.passdomain.cn", "192.0.2.2")
    print(ret)
