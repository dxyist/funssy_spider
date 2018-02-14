import requests
import json
from requests.adapters import HTTPAdapter

domain_url = "http://13.57.134.12:3001/api/v1.0"
convert_md5_url = "/login/convertMD5"
login_url = "/login/auth"
find_record_url = "/interface/record/findAll"
find_all_url = "/interface/rule/findAll"
max_retries = 200
time_out = 10

rs = requests.session();
rs.mount('http://', HTTPAdapter(max_retries=max_retries))
rs.mount('https://', HTTPAdapter(max_retries=max_retries))


def get_token():
    payload = {"key": "cootek"}
    r = rs.get(domain_url + convert_md5_url, params=payload, timeout=time_out)
    md5_str = r.json()["data"]['md5']
    r = rs.get(domain_url + login_url, params={"username": "xinyu.du@cootek.cn", "password": md5_str}, timeout=time_out)
    token_str = r.json()["data"]['token']
    return token_str


def get_ids(token_str, source_name, nation_name):
    r = rs.post(domain_url + find_all_url, data={"token": token_str}, timeout=time_out)
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
    r = rs.post(domain_url + find_record_url, data=post_dict, timeout=time_out)
    url_list = []
    for each in r.json()['data']['results']:
        url_list.append(each['url'])

    return url_list


if __name__ == '__main__':
    channel_list = get_channel_list('youtube_tops', 'United States of America')
    for each in channel_list:
        print(each)
    print(len(channel_list))
