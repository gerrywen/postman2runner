## 在Pypi上发布自己的Python包

- [Python的打包概述](https://packaging.python.org/overview/)
- [打包Python项目](https://packaging.python.org/tutorials/packaging-projects/#description)
- [在pypi上发布python包详细教程](http://www.mamicode.com/info-detail-2484744.html)


## 操作流程
- 1.创建用户验证文件
```linux
vi ~/.pypirc
```
```vim
[distutils]
index-servers=pypi

[pypi]
repository=https://upload.pypi.org/legacy/
username=用户名
password=密码
```

- 2.参考该项目的setup.py

- 3.项目打包
```shell
python3 setup.py sdist bdist_wheel
```

- 4.发布项目到Pypi
```shell
twine upload dist/*
```


