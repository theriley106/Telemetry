import http.client

conn = http.client.HTTPSConnection("http")

headers = {
    'nep-enterprise-unit': "String",
    'nep-correlation-id': "String",
    'nep-organization': "String"
    }

conn.request("GET", "//gateway-odsp-foundation-services.os1.ncrcloud.com/ias/item-availability/String", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
