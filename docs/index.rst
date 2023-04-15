.. xhs documentation master file, created by
   sphinx-quickstart on Tue Apr  4 09:56:35 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

xhs 用户文档
===============================

.. image:: https://img.shields.io/pypi/dm/xhs?style=for-the-badge
   :target: https://pypi.org/project/xhs/
   :alt: PyPI - Downloads

.. image:: https://img.shields.io/pypi/v/xhs?style=for-the-badge
   :target: https://pypi.org/project/xhs/
   :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/xhs?style=for-the-badge
   :target: https://pypi.org/project/xhs/
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/l/xhs?style=for-the-badge
   :target: https://pypi.org/project/xhs/
   :alt: PyPI - License

**xhs** 是一个封装小红书网页端的请求工具

**安装**::

   $ pip install xhs

**基础使用**::

   from xhs import XhsClient

   cookie = "请从网页端获取你的 cookie"
   xhs_client = XhsClient(cookie)

   # 获取笔记内容
   xhs_client.get_note_by_id("63db8819000000001a01ead1")

   # 获取用户信息
   xhs_client.get_user_info("5ff0e6410000000001008400")

   # 获取用户全部的笔记
   xhs_client.get_user_all_notes("63273a77000000002303cc9b")

   # 获取笔记全部的评论
   xhs_client.get_note_all_comments("63db8819000000001a01ead1")

   # 搜索笔记
   xhs_client.get_note_by_keyword("小红书")

   # 下载笔记图片或视频到指定路径下
   # 实际会下载到以笔记标题为文件夹名下
   # 例如：C:\Users\User\Desktop\笔记标题\图片.png
   xhs_client.save_files_from_note_id("63db8819000000001a01ead1",
                                       r"C:\Users\User\Desktop")

接口文档
-------------

初始化
^^^^^^^^
::

   xhs_client = XhsClient(cookie="", # 用户 cookie
                          user_agent="", # 自定义用户代理
                          timeout=10, # 自定义超时
                          proxies={}) # 自定义代理

获取笔记信息
^^^^^^^^^^^^^

``xhs_client.get_note_by_id("笔记ID")``

获取当前用户信息
^^^^^^^^^^^^^^^^^^

``xhs_client.get_self_info()``

获取用户信息
^^^^^^^^^^^^^

``xhs_client.get_user_info("用户ID")``

获取主页推荐
^^^^^^^^^^^^^^^^^^^

``xhs_client.get_home_feed(xhs.FeedType.RECOMMEND)``

搜索笔记
^^^^^^^^^^^^^
``xhs_client.get_note_by_keyword("搜索关键字")``

获取用户笔记
^^^^^^^^^^^^^
``xhs_client.get_user_notes("用户ID")``

获取笔记评论
^^^^^^^^^^^^
``xhs_client.get_note_comments("笔记ID")``

获取笔记子评论
^^^^^^^^^^^^^^^
``xhs_client.get_note_sub_comments("笔记ID", "父评论ID")``

评论笔记
^^^^^^^^^^^^^^^^
``xhs_client.comment_note("笔记ID", "评论内容")``

删除笔记评论
^^^^^^^^^^^^^^
``xhs_client.delete_note_comment("笔记ID", "评论ID")``

评论用户
^^^^^^^^^^^^^^^^^^
``xhs_client.delete_note_comment("笔记ID", "评论ID", "评论内容")``

关注用户
^^^^^^^^^^^^^^^^^^
``xhs_client.follow_user("用户ID")``

取关用户
^^^^^^^^^^^^^^^^^^
``xhs_client.unfollow_user("用户ID")``

收藏笔记
^^^^^^^^^^^^^^^^^^
``xhs_client.collect_note("笔记ID")``

取消收藏笔记
^^^^^^^^^^^^^^^^^^
``xhs_client.uncollect_note("笔记ID")``

点赞笔记
^^^^^^^^^^^^^^^^^^
``xhs_client.like_note("笔记ID")``

取消点赞笔记
^^^^^^^^^^^^^^^^^^
``xhs_client.dislike_note("笔记ID")``

点赞评论
^^^^^^^^^^^^^^^^^
``xhs_client.like_comment("笔记ID", "评论ID")``

取消点赞评论
^^^^^^^^^^^^^^^^^
``xhs_client.dislike_comment("评论ID")``

获取二维码
^^^^^^^^^^^^^^^^^
``xhs_client.get_qrcode()``

检查二维码状态
^^^^^^^^^^^^^^^^^^^^^
``xhs_client.check_qrcode("二维码ID", "二维码编码")``
