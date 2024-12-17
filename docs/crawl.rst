主页爬取
-------------

初始化
^^^^^^^^
::

   xhs_client = XhsClient(cookie="", # 用户 cookie
                          user_agent="", # 自定义用户代理
                          timeout=10, # 自定义超时
                          proxies={}) # 自定义代理

获取笔记信息
^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``xhs_client.get_user_notes("用户ID")``

获取用户收藏笔记
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``xhs_client.get_user_collect_notes("用户ID")``

获取用户点赞笔记
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``xhs_client.get_user_like_notes("用户ID")``

获取笔记评论
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``xhs_client.get_note_comments("笔记ID")``

获取笔记子评论
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``xhs_client.get_note_sub_comments("笔记ID", "父评论ID")``

评论笔记
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``xhs_client.comment_note("笔记ID", "评论内容")``

删除笔记评论
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``xhs_client.delete_note_comment("笔记ID", "评论ID")``

评论用户
^^^^^^^^^^^^^^^^^^
``xhs_client.comment_user("笔记ID", "评论ID", "评论内容")``

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
