### 商城项目

------

后端使用 Django 的 DRF 模块，提供 RESTful 风格的后端接口，前端使用 [XMall-Front-Simplify-Python](https://github.com/Lian-Zekun/XMall-Front-Simplify-Python)。



### 启动

------

1. 更改 setting 中数据库名称、用户以及密码。

2. 执行命令创建数据表

   ```shell
   python manage.py makemigrations
   python manage.py migrate
   ```

3. 项目的 docker 容器化并没有弄好，compose 目录下主要是在 [sentry官方github](https://github.com/getsentry/onpremise/releases/tag/20.12.1) 里下载 release 版本又加入了 elasticsearch，没有 mysql 的 docker 容器，sentry 中的 redis 可以设置映射外部端口，所有 docker 容器的启动利用 wsl 在 linux 环境运行 ./install.sh 启动。也可以暂时不启用 sentry，将 elasticsearch 配置单独运行使用，然后 setting 中设置自己的 mysql 以及 redis 配置。

4. 插入数据使用。下载[商品数据](https://pan.baidu.com/s/1EOTy9yTww_W7DlXGxx7Esw)，提取码 ehr0 。解压到 utils 目录下，单独运行 import.py 完成商品数据的导入，其他需要添加的部分随便找点图片设置一下。

5. ```sh
   python manage.py runserver
   ```



