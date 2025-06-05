from locust import task, run_single_user
from locust import FastHttpUser


class webapi(FastHttpUser):
    host = "https://xuece-stagingtest1.unisolution.cn"
    default_headers = {
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        "sec-ch-ua": '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    @task
    def t(self):
        with self.client.request(
            "GET",
            "/login",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Host": "xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/stuPaperList?from=nav",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/examcenter/student/exam/querylist_v2?pageNum=1&pageSize=10&nameLike=",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "a1e95034-642d-4328-9b4a-8cfc83153c00",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "POST",
            "https://utils.xuece.cn:8443/pluginwiris_engine/app/configurationjs",
            headers={
                "Accept": "*/*",
                "Content-Length": "0",
                "Host": "utils.xuece.cn:8443",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/nnauth/user/login?username=15861603019%40xuece&encryptpwd=c34dd995a8132605764a9347dae6e8ca&clienttype=BROWSER&clientversion=1.30.6&systemversion=chrome137.0.0.0",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "undefined",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/common/loginuserinfo/myinfo",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/basicdata/common/dictionary/listbytypes?dictTypes=USERTYPE%2CSCHOOLTYPE%2CGRADEPHASE%2CGRADE%2CEXAMTYPE%2CQUESTIONTYPE%2CTCHROLE",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/common/loginuserinfo/terminfo",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/common/loginuserinfo/terminfo/base",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/common/school/course/list?schoolId=76&year=2024&semester=SECOND",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/common/school/course/list?year=2025&semester=FIRST&schoolId=76",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/common/loginuserinfo/gatekeeper/list",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/teacher/permission/userpermission?includeReadOnly=false",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/teacher/permission/usergrade?withRole=true",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/teacher/permission/usergrade?withRole=true&year=2025&semester=FIRST",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/teacher/permission/userpermission?year=2025&semester=FIRST&includeReadOnly=false",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/common/loginuserinfo/modulepermission",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/usercenter/common/loginuserinfo/myschool",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/examcenter/operation_specialist/exam/inprogress",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://xuece-xqdsj-stagingtest1.unisolution.cn/api/holidayvideo/common/holidayvideo/isAuditor",
            headers={
                "Accept": "application/json, text/plain, */*",
                "AuthToken": "c5b675bc-ecef-45ca-9fd2-e19e0e27dbc2",
                "Host": "xuece-xqdsj-stagingtest1.unisolution.cn",
                "Origin": "https://xuece-stagingtest1.unisolution.cn",
                "Referer": "https://xuece-stagingtest1.unisolution.cn/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "XC-App-User-SchoolId": "76",
            },
        ) as resp:
            pass


if __name__ == "__main__":
    run_single_user(webapi)
