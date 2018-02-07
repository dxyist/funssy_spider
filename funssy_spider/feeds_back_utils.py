import requests
import json

domain_url = "http://120.26.41.89:3001/api/v1.0"
convert_md5_url = "/login/convertMD5"
login_url = "/login/auth"
find_record_url = "/interface/record/findAll"
find_all_url = "/interface/rule/findAll"


def get_token():
    payload = {"key": "cootek"}
    r = requests.get(domain_url + convert_md5_url, params=payload)
    md5_str = r.json()["data"]['md5']
    r = requests.get(domain_url + login_url, params={"username": "xinyu.du@cootek.cn", "password": md5_str})
    token_str = r.json()["data"]['token']
    return token_str


def get_ids(token_str, source_name, nation_name):
    r = requests.post(domain_url + find_all_url, data={"token": token_str})
    for each in r.json()['data']['results']:
        if each['sourceName'] == source_name:
            for country in each['countries']:
                na_str = " ".join(str(country['country'].encode('utf-8')).strip().split(' ')[:-1])
                if na_str == nation_name:
                    return country['ruleId'], country['id']
            return None, None


def get_channel_list(source_name, nation_name):
    token_str = get_token()
    rule_id, country_id = get_ids(token_str, source_name, nation_name)
    if rule_id is None or country_id is None:
        return []
    post_dict = {
        "token": token_str,
        "query": json.dumps({
            "ruleID": rule_id,
            "countryId": country_id
        })
    }
    r = requests.post(domain_url + find_record_url, data=post_dict)
    url_list = []
    for each in r.json()['data']['results']:
        url_list.append(each['url'])

    return url_list


if __name__ == '__main__':
    channel_list = get_channel_list('youtube', 'Thailand')
    for each in channel_list:
        print(each)
    print(len(channel_list))
