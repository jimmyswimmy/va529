import numpy as np
import robobrowser

class va529(object):

    site_base_url = "https://myaccount.virginia529.com"
    
    def __init__(self):
        self.browser = robobrowser.RoboBrowser(parser='lxml')
        
    def handle_redirect(self,content):
        result=content.find("meta",attrs={"http-equiv":"refresh"})
        if result:
            wait,text=result["content"].split(";")
            if text.strip().lower().startswith("url="):
                url=text[4:]
                return url
        return None
    
    def parse_table(self,table):
        """ Get data from table """
        return [
            [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
               for row in table.find_all('tr')
        ]

    def login(self,username,password):
        try:
            self.browser.open(self.site_base_url+"/pls/prod/twpkwbis.P_wwwlogin")
            
            login_form = self.browser.get_forms()[0]
            login_form['sid']=username
            login_form['PIN']=password
            self.browser.submit_form(login_form)
            # Returns a redirect as a meta:refresh tag; follow it to complete login
            content=self.browser.select('html')[0]
            new_url = self.handle_redirect(content)
            self.browser.open(self.site_base_url+new_url)
            if (self.browser.url != self.site_base_url+new_url):
                raise "Login failure."
            return
        except:
            return
    
    def get_account_list(self):
        # Now navigate to transaction data form
        self.browser.open(self.site_base_url+'/pls/prod/hwtkstmt.P_DispYearChoice')
        # Get the list of accounts from the drop down box
        options = self.browser.find_all('option')
        accounts = [ option.attrs['value'] for option in options]
        return accounts
    
    def get_transactions(self,account):
        self.browser.open(self.site_base_url+'/pls/prod/hwtkstmt.P_DispYearChoice')

        trans_form = self.browser.get_form()
        trans_form['cnum'] = account
        #print(account)
        self.browser.submit_form(trans_form)
        #print (self.browser.url)
        response_table = self.browser.find_all('table')[1]
        #print (response_table)
        data = self.parse_table(response_table)
        return np.array(data)

    def share_transactions(self, transaction_list):
        share_transaction_index = np.where(transaction_list[:,5]!='')
        return transaction_list[share_transaction_index]

if __name__=="__main__":
    username = ''
    password = ''
    m = va529(username,password)
    accounts = m.get_account_list()
    transactions = m.get_account_transactions(accounts[2])
    shares = m.share_transactions(transactions)
