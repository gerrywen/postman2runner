import io
import json
import logging
import os
import yaml
import re

from postman2runner import utils
from postman2runner.compat import ensure_ascii
from postman2runner.parser import parse_value_from_type


class PostmanParser(object):
    def __init__(self, postman_testcase_file):
        self.postman_testcase_file = postman_testcase_file

    def read_postman_data(self):
        """
        读取json数据
        :return:
        """
        with open(self.postman_testcase_file, encoding='utf-8', mode='r') as file:
            postman_data = json.load(file)

        return postman_data

    def parse_url(self, request_url):
        """
        解析请求地址
        :param request_url:
        :return:
        """
        url = ""
        if isinstance(request_url, str):
            url = request_url
        elif isinstance(request_url, dict):
            if "raw" in request_url.keys():
                url = request_url["raw"]
                url = self.postman2env(url)
        return url

    def parse_header(self, request_header):
        """
        头部数据解析处理
        :param request_header:
        :return:
        """
        headers = {}
        for header in request_header:
            _value = header["value"]
            _value = self.postman2env(_value)
            headers[header["key"]] = _value
        return headers

    def postman2env(self, _value):
        """
        postman的环境变量参数名转py环境变量名
        :param _value:
        :return:
        """
        value_split = _value.split("}}", 1)
        _url = ''
        if len(value_split) > 1:
            _url = value_split[1]
        p1 = re.compile(r'{{(.*?)}}', re.S)  # 最小匹配
        value_list = re.findall(p1, _value)
        if len(value_list) > 0:
            _value = "${ENV(" + value_list[0] + ")}"
            _value += _url
        return _value

    def parse_api_uri(self, url):
        """
        获取接口地址
        :param url:
        :return:
        """
        url_split = url.split(")}", 1)
        _url = ''
        if len(url_split) > 1:
            _url = url_split[1]
        else:
            url_split = url.split("/")[-1]
            if len(url_split) > 1:
                _url = url_split[1]
            else:
                _url = url
        _url = _url.replace('/', '_')
        return _url

    def dict_format(self, dict_obj, dict_tmp={}):
        """
        对raw数据提交进行格式化
        :param dict_obj:
        :param dict_tmp:
        :return:
        """
        dict_list = []
        if (type(dict_obj).__name__ == 'dict'):
            list_tmp = []
            for k, v in dict_obj.items():
                tmp = {'key': k, 'value': v, 'type': 'text'}
                list_tmp.append(tmp)
                self.dict_format(v, tmp)
                dict_tmp['value'] = list_tmp
            dict_list.append(list_tmp)
            return list_tmp
        return dict_list

    def parse_each_item(self, item):
        """ parse each item in postman to testcase in httprunner
        """
        api = {}
        api["name"] = item["name"]
        api["validate"] = [
            {
                "eq": ['status_code', 200]
            },
            {
                "eq": ['headers.Content-Type', 'application/json']
            }
        ]
        api["variables"] = []

        request = {}
        request["method"] = item["request"]["method"]

        url = self.parse_url(item["request"]["url"])

        if request["method"] == "GET":
            request["url"] = url.split("?")[0]
            request["headers"] = self.parse_header(item["request"]["header"])

            body = {}
            if "query" in item["request"]["url"].keys():
                for query in item["request"]["url"]["query"]:
                    api["variables"].append({query["key"]: parse_value_from_type(query["value"])})
                    body[query["key"]] = "$" + query["key"]
            request["params"] = body
        else:
            request["url"] = url
            request["headers"] = self.parse_header(item["request"]["header"])

            body = {}
            if ("body" in item["request"].keys()) and (item["request"]["body"] != {}):
                mode = item["request"]["body"]["mode"]
                # 判断是不是row类型的请求参数
                if mode == 'raw' and len(item["request"]["body"][mode]) > 0:
                    raw = item["request"]["body"][mode]
                    # print(raw)
                    raw = json.loads(raw)
                    raw_list = self.dict_format(raw)
                    # print(raw_list)
                    item["request"]["body"][mode] = raw_list
                if isinstance(item["request"]["body"][mode], list):
                    for param in item["request"]["body"][mode]:
                        if param["type"] == "text":
                            api["variables"].append({param["key"]: parse_value_from_type(param["value"])})
                        else:
                            api["variables"].append({param["key"]: parse_value_from_type(param["src"])})
                        body[param["key"]] = "$" + param["key"]
                elif isinstance(item["request"]["body"][mode], str):

                    body = item["request"]["body"][mode]
            request["data"] = body

        api["request"] = request
        return api

    def parse_items(self, items, folder_name=None):
        """
        解析每个items数据
        :param items:
        :param folder_name:
        :return:
        """
        result = []
        for folder in items:
            if "item" in folder.keys():
                name = folder["name"].replace(" ", "_")
                if folder_name:
                    name = os.path.join(folder_name, name)
                # 递归读取下一级item
                temp = self.parse_items(folder["item"], name)
                result += temp
            else:
                api = self.parse_each_item(folder)
                api["folder_name"] = folder_name
                result.append(api)
        return result

    def parse_data(self):
        """
        dump postman data to json testset
        """
        logging.info("Start to generate JSON testset.")
        #  读取json数据
        postman_data = self.read_postman_data()
        # 提取postman item数据
        result = self.parse_items(postman_data["item"], None)
        return result

    def save(self, data, output_dir, output_file_type="json"):
        count = 0
        output_dir = os.path.join(output_dir, "api")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for each_api in data:
            count += 1
            try:
                api_uri = self.parse_api_uri(each_api['request']['url'])
            except:
                api_uri = str(count)
            file_name = api_uri + "." + output_file_type

            folder_name = each_api.pop("folder_name")
            if folder_name:
                folder_path = os.path.join(output_dir, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                # 文件输入写入路径
                file_path = os.path.join(folder_path, file_name)
            else:
                # 文件输入写入路径
                file_path = os.path.join(output_dir, file_name)
            # 判断文件路径是否存在
            if os.path.isfile(file_path):
                logging.error("{} file had exist.".format(file_path))
                continue
            # 判断输出类型
            if output_file_type == "json":
                utils.dump_json(each_api, file_path)
                # with io.open(file_path, 'w', encoding="utf-8") as outfile:
                #     my_json_str = json.dumps(each_api, ensure_ascii=ensure_ascii, indent=4)
                #     if isinstance(my_json_str, bytes):
                #         my_json_str = my_json_str.decode("utf-8")
                #
                #     outfile.write(my_json_str)
            else:
                utils.dump_yaml(each_api, file_path)
                # with io.open(file_path, 'w', encoding="utf-8") as outfile:
                #     my_json_str = json.dumps(each_api, ensure_ascii=ensure_ascii, indent=4)
                #     yaml.dump(each_api, outfile, allow_unicode=True, default_flow_style=False, indent=4)
