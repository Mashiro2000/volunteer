# <p align="center">volunteer</p>
<p align="center">活动已下架(2021-12-01)</P>
<p align="center">第一次成功反编译出Signature算法😊</P>
<p align="center">喜欢这个项目？可以在右上角给颗⭐！你的支持是我最大的动力😎！</P>

## 免责声明
- 本仓库发布的volunteer项目中涉及的任何脚本，仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断.

- 所有使用者在使用volunteer项目的任何部分时，需先遵守法律法规。对于一切使用不当所造成的后果，需自行承担.对任何脚本问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害.

- 如果任何单位或个人认为该项目可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，我们将在收到认证文件后删除相关文件.

- 任何以任何方式查看此项目的人或直接或间接使用该volunteer项目的任何脚本的使用者都应仔细阅读此声明。本人保留随时更改或补充此免责声明的权利。一旦使用并复制了任何相关脚本或volunteer项目的规则，则视为您已接受此免责声明.

您必须在下载后的24小时内从计算机或手机中完全删除以上内容.

> 您使用或者复制了本仓库且本人制作的任何脚本，则视为`已接受`此声明，请仔细阅读

## 环境

[Python3](https://www.python.org/) >= 3.6

## 已实现功能
* [x] 每日登录
* [x] 观看志汇学院视频
* [x] 小课堂答题
* [x] 飞船充能(需自行绑定学校) 
* [x] 推送通知 

## 文件说明
```text
│  index.py             # 活动脚本
│  account.py           # 账号文件
│  sendNotify.py        # 推送文件
│  README.md            # 说明文档
```

## 青龙命令
```text
第一次拉库命令
ql repo https://github.com/Mashiro2000/volunteer.git "" "account|sendNotify" "account|sendNotify"
第二次拉库命令(确保account.py不被覆盖)
ql repo https://github.com/Mashiro2000/volunteer.git "" "account|sendNotify" "sendNotify"
```
## 特别说明
> 感谢舍友[@subcarry](https://github.com/subcarry)合作开发本项目
