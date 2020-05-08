from kivy.app import App
from kivy.uix.button import Button

class TestApp(App):
    def build(self):
        return Button(text='Hello World')
 
TestApp().run()
————————————————
版权声明：本文为CSDN博主「天生少数派」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/java_xinxiu/article/details/103488873