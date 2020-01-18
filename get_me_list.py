import requests
import re
import json


def get_follower_or_following(target_username, follower_or_following):
    settings = {
        "follower": {"hash": "c76146de99bb02f6415203be841dd25a", "edge_name": "edge_followed_by"},
        "following": {"hash": "d04b0a864b4b54837c0d870b0e77e076", "edge_name": "edge_follow"},
        "my_username": my_username, "my_password": my_password}
    
    try:
        query_hash = settings[follower_or_following]["hash"]
    except:
        return {"message": "Wrong argument. It must be 'follower' or 'following'", "users": []}

    try:
        s = requests.Session()
        r = s.get("https://www.instagram.com/")
        csrf_token = re.search('"csrf_token":"(.*?)"', r.text)[1]
        s.headers.update({"X-CSRFToken": csrf_token})
        my_username = settings["my_username"]
        my_password = settings["my_password"]
        login_post_data = {"username": my_username, "password": my_password}
        login_response = s.post("https://www.instagram.com/accounts/login/ajax/", data=login_post_data).json()
        auth = login_response["authenticated"]
    except:
        auth = False
    if not auth:
        return {"message": "login failed", "users": []}
    try:
        resp = s.get("https://www.instagram.com/" + target_username)
        resp_code = resp.status_code
    except:
        resp_code = "https://www.youtube.com/watch?v=lHYC06HzCrg"
    if resp_code != 200:
        return {"message": "Wrong target name or bad internet connection", "users": []}
    
    data_text = re.search('window._sharedData = (.*?);</script>', resp.text)[1]
    data = json.loads(data_text)
    target_id = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
    users = []
    end_cursor = "first_attemp"
    while True:
        if end_cursor == "first_attemp":
            query_variables = '{"id":"%s","first":24}' % target_id
        else:
            query_variables = '{"id":"%s","first":50,"after":"%s"}' % (target_id, end_cursor)
        payload = {"query_hash": query_hash, "variables": query_variables}
        try:
            r = s.get('https://www.instagram.com/graphql/query/?', params=payload)
            edge = settings[follower_or_following]["edge_name"]
            edge_data = r.json()["data"]["user"][edge]
            end_cursor = edge_data["page_info"]["end_cursor"]
        except:
            return {"message": "Couldn't reach full data :( maybe your query hash is not valid", "users": []}
        for user_raw_data in edge_data["edges"]:
            user_id = user_raw_data["node"]["id"]
            username = user_raw_data["node"]["username"]
            fullname = user_raw_data["node"]["full_name"]
            users.append({"user_id": user_id, "username": username, "fullname": fullname})
        if end_cursor is None:
            break
    return {"message": "success", "users": users}
