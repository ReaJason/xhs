快速入门
===============================

由于 x-s 签名较复杂，因此使用 `playwright <https://playwright.dev/python/>`_ 进行模拟浏览器行为进行 js 函数调用获取签名算法，
并且其中存在大量的环境检测的行为，因此需要使用到 `stealth.min.js <https://github.com/requireCool/stealth.min.js>`_ 进行绕过。

**环境安装**:

.. code-block:: bash

    pip install xhs # 下载 xhs 包

    pip install playwright # 下载 playwright

    playwright install # 安装浏览器环境

    curl -O https://cdn.jsdelivr.net/gh/requireCool/stealth.min.js/stealth.min.js # 下载 stealth.min.js

基础使用
-----------
请注意 cookie 的获取，a1、web_session 和 webId 三个字段为必需字段。

具体代码参考：`basic_usage.py <https://github.com/ReaJason/xhs/blob/master/example/basic_usage.py>`_


进阶使用
----------------
将 playwright 封装为服务端，主函数使用 requests 请求，获取签名，多账号使用统一签名服务请确保 cookie 中的 a1 字段统一，防止签名一直出现错误


环境安装
^^^^^^^^^^^^^^^^^^^^^^

可以直接使用 Docker 来起下面的 Flask 服务，然后使用 XhsClient 即可，服务启动会打印 a1，推荐将自己的 cookie 中的 a1 与服务端设置成一致

.. code-block:: bash

    docker run -it -d -p 5005:5005 reajason/xhs-api:latest

如果在本机启动 Flask 需要安装如下依赖：

.. code-block:: bash

    pip install flask, gevent, requests

开启 Flask 签名服务
^^^^^^^^^^^^^^^^^^^^^^^^
具体代码参考： `basic_sign_server <https://github.com/ReaJason/xhs/blob/master/example/basic_sign_server.py>`_


使用 XhsClient
^^^^^^^^^^^^^^^^^^^

具体代码参考： `basic_sign_usage <https://github.com/ReaJason/xhs/blob/master/example/basic_sign_usage.py>`_
