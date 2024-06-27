#设置python环境镜像
FROM python:3.9
#代码添加到Chenge文件夹，code不需要新建（docker执行时自建）
ADD . /pycode
# 设置code文件夹是工作目录
WORKDIR /pycode
EXPOSE 34555
# 安装相应的python库RUN 
RUN pip3 install -r requirements.txt

CMD ["python", "/pycode/app.py"]