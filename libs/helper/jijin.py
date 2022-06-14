import requests
import json
from graia.ariadne.message.chain import MessageChain  # 信息链

def jj_message_chain(res):
    """return a message chain from raw results"""
    return MessageChain(
        (f"{res['data'][0]['name']} ({res['data'][0]['code']})\n")
        + (f"日涨跌幅: {(res['data'][0]['dayGrowth'])}%\n")
        + (f"预计今日涨幅: {(res['data'][0]['expectGrowth'])}%")
    )

def jj_search(jj_code):
    """return jj raw results from API search"""
    jj_url = 'https://api.doctorxiong.club/v1/fund/detail/list'
    jj_req_params = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    jj_req_params['code'] = jj_code
    res = requests.get(jj_url, params=jj_req_params, headers=headers)
    
    search_result = json.loads(res.text)
    if 'data' not in search_result:
        return None
    else:
        return jj_message_chain(search_result)