class Test(object):
    
    def __init__(self):
        self.length = 5

    def set_length(self, length):
        if length < 15:
            self.length = length
        else:
            self.length = 15

t = Test()
print(t.length)
t.set_length(23)
print(t.length)
print("hallo")
