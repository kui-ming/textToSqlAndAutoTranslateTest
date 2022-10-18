举例：
用户
id、用户名 密码 盐值

自动转换

```sql
create table(
    id int(11) primary key auto_increment,
    username varchar(255) not null,
    password varchar(32) not null,
    salt varchar(32) not null
)
```
