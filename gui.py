import wx

app = wx.App()
frame = wx.Frame(None, title="Gui Test Editor", pos=(1000, 200), size=(500, 400))

path_text = wx.TextCtrl(frame, pos=(5, 5), size=(350, 24))
open_button = wx.Button(frame, label="打开", pos=(370, 5), size=(50, 24))
save_button = wx.Button(frame, label="保存", pos=(430, 5), size=(50, 24))

content_text= wx.TextCtrl(frame,pos = (5,39),size = (475,300),style = wx.TE_MULTILINE)
# wx.TE_MULTILINE可以实现换行功能,若不加此功能文本文档显示为一行显示

frame.Show()
app.MainLoop()