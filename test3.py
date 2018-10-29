import requests
import base64

base_url = "https://hackgt-api.ncrcloud.com/"
api_key = "8a82859f5ef21870015ef2fa5e5f0000"
enterprise_key = "eafe5b77b5594e9ab575ed4b41d6ee37"
org = "/org-1/"

def getAuthKey():
	url = base_url + "security/authentication/login"
	encoded = base64.b64encode("acct:org-1@admin:Chang3m3!!-admin-org-1")
	header = {
		"Authorization": "Basic " + encoded,
		"nep-application-key": api_key
	}
	r = requests.post(url, headers=header)
	return r.json()["token"]

def getItemFromDB(item_name):
	lines = [line.strip("\n") for line in open("item_data.txt")]
	for line in lines:
		l = line.split(',')
		if (l[1] == item_name):
			return l[0]

def getItem(item_name):
	itemCode = getItemFromDB(item_name)

	url = base_url + "catalog/items/" + itemCode
	auth_key = getAuthKey()

	headers = {
		"authorization": "AccessToken " + auth_key,
		"cache-control": "no-cache",
		"nep-organization": org,
		"nep-application-key": api_key,
		"Accept": "application/json, text/plain, */*",
		"Content-Type": "application/json"
	}

	r = requests.get(url, headers=headers)
	return { "itemCode": itemCode, "item_name_long": r.json()["longDescription"]["values"][0]["value"] }

def getItemPrice(itemCode):
	url = base_url + "catalog/item-prices/" + itemCode + "/" + itemCode
	auth_key = getAuthKey()

	headers = {
		"authorization": "AccessToken " + auth_key,
		"cache-control": "no-cache",
		"nep-organization": org,
		"nep-application-key": api_key,
		"Accept": "application/json, text/plain, */*",
		"Content-Type": "application/json",
		"nep-enterprise-unit": "eafe5b77b5594e9ab575ed4b41d6ee37"
	}

	r = requests.get(url, headers=headers)
	return r.json()["price"]

if __name__ == '__main__':
	print getItemPrice("33120")
