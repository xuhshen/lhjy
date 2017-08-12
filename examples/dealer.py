from rest_framework.exceptions import ErrorDetail, ValidationError

def backendupdate(ticket):
    pass

def order2securities(data):
    '''下单到券商
    '''
    ticket=111
    action = data.get("action")
    code = data.get("code")
    account = data.get("account")
    
    try:
        print (data)
    except:
        raise ValidationError({"error":1,"message":"ordering failed"})
    
    return ticket

class fundaccount(object):
    def __init__(self,username,passwd):
        pass

    def login(self):
        pass
    
    def logout(self):
        pass

    
    
    
    
def buy(data):
    pass

def sell():
    pass

