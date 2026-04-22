WeChat Message Sender

This package is ready to use.
The end user does NOT need to install Python or build anything.
The default release now uses a single offline exe to keep the file count low.

How to use:

1. Make sure desktop WeChat is installed, logged in, and visible.
2. Open a terminal in this folder.
3. Run one of the commands below.

Send a message:
.\wechat-message-sender.exe --who "Zhang San" --message "Hello"

List visible WeChat sessions:
.\wechat-message-sender.exe --list-sessions

Notes:
- Fuzzy matching is supported for contact and group names, but a more complete visible session name is still recommended.
- The tool switches back to the chat page and prefers clicking visible sessions or search results before falling back to backend APIs.
- Send success is verified against the raw chat bubble list in the target conversation.
- If WeChat 4.x cannot be read, set QT_ACCESSIBILITY=1, fully exit WeChat, and open it again.
