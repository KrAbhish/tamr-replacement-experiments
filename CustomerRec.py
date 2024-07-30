import csv
import re
import editdistance
import numpy as np

comp_variants=['limited', 'inc', 'corp', 'llc', 'gmbh', 'plc', 'privatelimited', 'privateltd', 'pvtltd']
class LegalMaster:
    def clean_phone_number(self, number):
        return re.sub("[^0-9]", "", number)

    def clean(self, name):
        return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

    def clean_name(self, name):
        name = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
        for pattern in comp_variants:
            name = name.replace(pattern, 'ltd')
        return re.sub(r'[^a-zA-Z0-9]', '', name)
    
    def __init__(self, name, taxes, bvds, phone, cntrycode, city, state):
        self.onames = [name]
        self.names = [self.clean_name(name)]
        self.taxes = []
        self.cntrycode = cntrycode
        self.ocity = city
        self.city = self.clean(city)
        self.ostate = state
        self.state = self.clean(state)
        for itm in taxes:
            self.taxes.append(itm)
        self.bvds = []
        for itm in bvds:
            self.bvds.append(itm)
        self.phones = [self.clean_phone_number(phone)]

    def to_string(self):
        max_idx = max(max(max(len(self.names),len(self.taxes)),len(self.bvds)),len(self.phones))
        lines = []
        for i in range(max_idx):
            line=',,,,,'
            if i < len(self.onames):
                line+=self.onames[i]
            line+=',,,,,,,'+self.ocity+',,,'+self.ostate+','+self.cntrycode+',,,,,'
            if i < len(self.phones):
                line+=self.phones[i]
            line+=',,'
            if i < len(self.bvds):
                line+=self.bvds[i]
            line+=','
            if i < len(self.taxes):
                line+=self.taxes[i]
            lines.append(line)
        return lines

    def add_taxes(self, arr):
        for itm in arr:
            if 'null' in itm:
                continue
            if itm not in self.taxes:
                self.taxes.append(itm)
    
    def add_bvd(self, arr):
        for itm in arr:
            if 'null' in itm:
                continue
            if itm not in self.bvds:
                self.bvds.append(itm)
    
    def add_phone(self, phn):
        phn = self.clean_phone_number(phn)
        if phn not in self.phones:
            self.phones.append(phn)

    def add_name(self, name):
        nm = self.clean_name(name)
        if nm not in self.names:
            self.names.append(nm)
            self.onames.append(name)
    
    def name_cntry_match(self, name, cntry):
        if self.cntrycode == cntry:
            for itm in self.names:
                dist = editdistance.eval(name,itm)
                perc = dist/len(name)
                if perc <= .3:
                    return True
        return False

    def name_phn_match(self, name, phn):
        min_name = 100
        for itm in self.names:
            dist = editdistance.eval(name,itm)
            perc = dist/len(name)
            if perc <= .2 and perc < min_name:
                min_name = perc
        min_phn = 100
        for itm in self.phones:
            dist = editdistance.eval(phn,itm)
            perc = dist/len(phn)
            if perc <= .25 and perc < min_phn:
                min_phn = perc
        if min_name <= .2 and min_phn <= .25:
            return True
        return False

    def name_city_match(self, name, city, isCity=True):
        min_name = 100
        for itm in self.names:
            dist = editdistance.eval(name,itm)
            perc = dist/len(name)
            if perc <= .2 and perc < min_name:
                min_name = perc
        min_phn = 100
        if isCity == True:
            dist = editdistance.eval(self.city,city)
        else:
            dist = editdistance.eval(self.state,city)
        if min_name <= .2 and dist <= .2:
            return True
        return False
    
    def match_taxes(self, taxes):
        for itm in taxes:
            if 'null' in itm:
                continue
            for tx in self.taxes:
                dist = editdistance.eval(itm,tx)
                perc = dist/len(itm)
                if perc <= .1:
                    return True
        return False

    def match_bvds(self, bvds):
        for itm in bvds:
            if 'null' in itm:
                continue
            for tx in self.bvds:
                dist = editdistance.eval(itm,tx)
                perc = dist/len(itm)
                if perc <= .1:
                    return True
        return False

#    def name_match2(self, nm):
        
    def match(self, arr):
        nm = self.clean_name(arr[4])
        txnos = arr[27:33]
        bvds = arr[24:27]
        city = self.clean(arr[11])
        state = self.clean(arr[14])
        for itm in self.names:
            dist = editdistance.eval(nm,itm)
            perc = dist/len(nm)
            if perc <= .1:
                return True
        for itm in txnos:
            if 'null' in itm:
                continue
            if itm in self.taxes:
                return True
        for itm in bvds:
            if 'null' in itm:
                continue
            if itm in self.bvds:
                return True
        if self.cntrycode == arr[15]:
            for itm in self.phones:
                if itm == arr[21]:
                    return True
        if self.name_cntry_match(nm, arr[15]) is True:
            return True
        if self.name_phn_match(nm, arr[21]) is True:
            return True
        if 'null' not in city and self.name_city_match(nm, city) is True:
            return True
        if 'null' not in city and self.name_city_match(nm, state, False) is True:
            return True
        if self.match_taxes(txnos) is True:
            return True
        if self.match_bvds(txnos) is True:
            return True
        #print('-----'+nm)
        #print(self.names)
        return False
