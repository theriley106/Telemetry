import requests

def get_item_availability(search_item):
    url = "https://gateway-staging.ncrcloud.com/catalog/items"

    querystring = {"pageNumber":"0","pageSize":"200","longDescriptionPattern":("%2A " + search_item)}

    headers = {
        'nep-application-key': "8a00860b6641a0ae0166471356ba000f",
        'accept': "application/json",
        'content-type': "application/json",
        'Authorization': "Basic YWNjdDpqYW1AamFtc2VydmljZXVzZXI6MTIzNDU2Nzg=",
        'Cache-Control': "no-cache",
        'Postman-Token': "d25fe7bb-7340-45ef-ab07-76205c9097f8"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_dict = response.json()

    item_code_list = []
    item_name_list = []
    # load item_code's into list
    for i in range(0, len(response_dict['pageContent'])):
        item_name_list.append(response_dict['pageContent'][i]['longDescription']["value"])
        item_code_list.append(response_dict['pageContent'][i]['itemId']['itemCode'])
    if len(item_code_list) > 0:
        return True
    else:
        return False

def full_response(search_item):
    response = ""
    if get_item_availability(search_item) == True:
        response += search_item + " is currently available at the HackGT store."
    else:
        response += search_item + " is currently out of stock at the HackGT store."
    return response


if __name__ == '__main__':
    #print getin("33120")
    print get_item_availability("soda")



