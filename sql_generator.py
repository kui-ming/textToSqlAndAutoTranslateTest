import json

"""
将数据表集合对象解析为SQL语句，然后才能导入数据库
"""


def parse_type(field) -> str:
    """
    解析字段对象中的数据类型属性，主要是对数据类型进行纠错和补全
    :param tp: str,数据类型
    :return: str,规范化后的数据类型
    """
    tp = field.get('type').lower()
    len = field.get('len')
    # 错别字改正
    if tp in ['varcher', 'varcahr']:
        tp = 'varchar'

    # 添加长度
    if 'int' == tp:
        if not len:
            len = 11
        tp += f'({len})'
    elif 'varchar' == tp:     # 字符串varchar没有指定长度，默认设置为255
        if not len:
            len = 255
        tp += f'({len})'
    elif tp == "enum":      # 枚举没有设置值
        tp = "enum('0','1')"
    return tp


def parse_default(default) -> str:
    """
        解析字段默认值
        :param default:
        :return:
    """
    sql = ''
    try:
        default = int(default)  # 可解析为整数
        sql = f"default {default} "
    except ValueError:
        if default in ['CURRENT_TIMESTAMP']:
            sql = f"default {default} "
        else:
            sql = f"default '{default}' "  # 解析默认值为字符串
    return sql


def parse_column(table) -> str:
    """
    解析数据表集合对象中的数据表对象中的字段集合对象，将每个字段对象解析为一行SQL语句，放在创建表的SQL语句中
    :param table: 数据表对象
    :return: stt,一行创建字段用的SQL语句
    """
    sql = ''
    table = dict(table)
    columns = table.get('fields', [])
    for col in columns:
        col_name = col['name']
        col_type = parse_type(col)
        additional = ''
        if not col['is_null'] and not col['primary_key']:   # 非空并且不是主键时
            additional += 'not null '
        elif col.get('primary_key'):    # 为主键时
            additional += 'primary key '
        if col.get('default'):  # 默认值存在时
            additional += parse_default(col['default'])     # 解析默认值为字符串
        if col.get('additional'):   # 附加值存在时，直接加上
            additional += col['additional'] + ' '
        sql += f'''       {col_name} {col_type} {additional} comment '{col["remark"]}',\n'''
    if sql != '':
        sql = sql[:-2] + '\n'
    return sql


def to_sql(obj) -> str:
    """
    接收字典类型的数据表集合对象，将其解析为字符串类型的SQL语句，方便导入数据库
    :param obj: 数据表集合对象
    :return: str,返回字符串格式的SQL语句
    """
    sql_text = ''
    try:
        if type(obj) == str:
            obj = json.loads(obj)   # 尝试将字符串解析为字典
    except Exception:
        pass
    if not (type(obj) == dict and obj.get('tables')):   # 如果接收的形参不是该格式则返回空字符串
        return sql_text
    # 开始生成
    for table in obj['tables']:
        create_table_sql = f'create table if not exists {table["name"]}(\n'
        create_table_sql += parse_column(table)
        create_table_sql += f") comment='{table['comments']}';\n\n\n"
        sql_text += create_table_sql
    return sql_text
