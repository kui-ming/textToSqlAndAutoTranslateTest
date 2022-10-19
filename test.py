#
import tools
from baidu_translate_test import translate_test as trans
import re
import sql_generator


# 接收
def start():
    origin = ""
    with open('text.txt', 'r', encoding="utf-8") as f:
        origin = f.read()
    return parse(origin)


# 解析为对象
def parse(text):
    table_obj = {
        'name': '',
        'comments': '',
        'fields': []
    }
    #   处理源文本
    text = text.replace("、", ",")
    text = text.replace("，", ",")
    #   将字符串分割，试图找出表名与字段名
    text = text.split('\n')
    table = text[0]
    fields = text[1]
    #   解析表名
    if tools.is_contains_chinese(text):     # 包含中文
        table_obj['comments'] = table
    else:
        table_obj['name'] = table
    #   解析字段
    fields = fields.split(",")
    for field in fields:
        field_obj = {"name": '', "remark": ""}
        if tools.is_contains_chinese(field):
            field_obj["remark"] = field
        else:
            field_obj["name"] = field
        table_obj['fields'].append(field_obj)
    print(table_obj)
    translate_table(table_obj)
    return table_obj


# 翻译字段
def translate_table(table_obj: dict):
    #   翻译表名
    word = str(table_obj.get("name"))
    if not word:   # 表名为空或为''
        res = trans.translate(table_obj.get('comments'))
        word = str(res['trans_result'][0].get("dst"))
    else:
        #   通过英文表名翻译中文备注
        res = trans.translate(word, True)
        table_obj['comments'] = str(res['trans_result'][0].get("dst"))
    word = word.lower().strip().replace(" ", "_")
    table_obj['name'] = word
    #   翻译字段名
    for field in table_obj.get('fields'):
        word = str(field['name'])
        if not word:
            res = trans.translate(field.get('remark'))
            word = str(res['trans_result'][0].get("dst"))
        else:
            #   通过英文字段名翻译中文备注
            res = trans.translate(word, True)
            field['remark'] = str(res['trans_result'][0].get("dst"))
        word = word.lower().strip().replace(" ", "_")
        field['name'] = word
    is_type(table_obj)
    #   返回翻译后的对象
    return table_obj


# 判断字段类型
def is_type(table_obj: dict):
    fields = table_obj.get("fields")
    is_find_key = True
    for field in fields:
        name = field.get('name')
        # 判断是否具有Type
        if not field.get('type'):
            if name[-2:] == "id":
                field['type'] = 'int'
            elif name[-4:] == "time":
                field['type'] = 'datetime'
            else:
                field['type'] = 'varchar'
        # 是否存在长度
        if not field.get('len'):
            field_type = field.get('type')
            if field_type == 'int':
                field['len'] = 11
            elif field_type == 'varchar':
                field['len'] = 255
        # 是否为主键
        if not field.get('primary_key') and is_find_key:
            if name[-2:] == 'id':
                field['primary_key'] = True
                is_find_key = False
        # 是否为空
        if not field.get("is_null"):
            if field.get("primary_key"):
                field['is_null'] = False
            else:
                field['is_null'] = True
    # 如果字段循环完毕还未找到主键，直接将第一个字段设置为主键
    if not is_find_key:
        table_obj.get('fields')[0]['primary_key'] = True
    return table_obj


# 生成SQL
def generate_sql(table_obj: dict):
    return sql_generator.to_sql({'tables': [table_obj]})


print(generate_sql(start()))
