import zipfile,tarfile
import shutil
import os
import logging
import time
 
global logger
def start(startpath,endpath,log):
    global logger
    try:
        logging.basicConfig(filename=log+'\LOG.log',
                            format='%(asctime)s %(message)s',
                            filemode='w')
        # Creating an object
        logger = logging.getLogger()         
        # Setting the threshold of logger to DEBUG
        logger.setLevel(logging.DEBUG)
    except:
        logging.basicConfig(filename="LOG.log",
                            format='%(asctime)s %(message)s',
                            filemode='w')
        # Creating an object
        logger = logging.getLogger()         
        # Setting the threshold of logger to DEBUG
        logger.setLevel(logging.DEBUG)
    
    if(startpath==''):
        print("No Path Input")        
        return
    if(endpath==''):
        print("No target Path")
        return
    for root, dirs, files in os.walk(startpath):
        for file in files:
            if(file.endswith(".gz")):
                loc,name,onecom = changename(root, file)       
                try:
                    if(move(loc, endpath,name,onecom)):
                        print(file," : Complete")                   
    
                    else:
                        print(file," : Fail ")
                    pass
                except Exception as e:
                    print(e)
                    pass
                
    
def changename(filepath,fname):
    global logger
    print("CHANGING NAME")
    archive = tarfile.open(filepath + '/' + fname,'r')
    #print(archive.name)
    for member in archive.getmembers():

        memtmp = member.name.split("_")
        #================Change Name================================
        print("member : ", member.name)
        if (member.name.endswith('.h5')):
            ENDWITH = '_1'
        if (member.name.endswith('.tgz')):
            ENDWITH = '_2'
        if(memtmp[0] == "./DFDN"):         
        #==================extract==============================           
            archive.extract(member,filepath)
        #=========================CRC Checking 1's Complitment======================
            fileLocation = filepath + '/' + member.name[2:]           
            one_compliment = initCRC_Return_1sCompliment(fileLocation)
            os.remove(filepath + '/' + member.name[2:])         
        #============================================================    
            newName = member.name.replace(".h5.xml", "")
            newName = newName.replace("./DFDN_", "")         
            oldname = archive.name
        
    newName = newName + ENDWITH
    archive.close()
    #print("---------------")       
    os.rename(oldname, filepath + "/" + newName + ".tar.gz")
    fileloc = filepath + "/" + newName + ".tar.gz"
    #print(newName)
    logger.info(fname + " change to " + newName)
    return fileloc,newName+".tar.gz", one_compliment

def move(loc,despath,name,onecom):
    global logger
    print("MOVING")
    tmplist = name.split("_")
    if not(os.path.exists(despath + '/' + tmplist[8][0:4] + '/' + name)):
        try:
            shutil.move(loc, despath + '/' + tmplist[8][0:4] + '/' + name)
            logger.info("moving file : " + name + " to " + despath)
        except:
            os.makedirs(despath + '/' + tmplist[8][0:4] + '/')
            shutil.move(loc, despath + '/' + tmplist[8][0:4] + '/' + name)
            logger.info("moving file : " + name + " to " + despath)
    else:
        os.remove(loc)
        print("FILE EXIST")
        logger.info(" file : " + name + ' is Exist')
        return
    
    try:
        archive = tarfile.open(despath + '/' + tmplist[8][0:4] + '/' + name,'r')
        #print(archive.name)
        for member in archive.getmembers():
    
            memtmp = member.name.split("_")
            if(memtmp[0] == "./DFDN"):         
            #==================extract==============================

                archive.extract(member,loc)
    
            #=========================CRC Checking ======================
                fileLocation = loc + '/' + member.name[2:]           
                ans = initCRC_Return_True(fileLocation,onecom)
                shutil.rmtree(loc)
            
        archive.close()
        if (ans):
            print("Moving : ", name, "Complete")
            logger.info("File : " + name + ' Complete')
            return True
        else:
            print("Moving : ", name, "CRC Fail")
            logger.info("File : " + name + ' Complete')            
                   
            print("NOT TRUE")
            #==================IF FAIL==========================
            try:                    
                shutil.move(despath + '/' + tmplist[8][0:4] + '/' + name, "./ERROR_Detected/" + name)
                logger.error(name + " : CRC Failed")
            except:
                print("Creating Folder ERR")
                os.makedirs("./ERROR_Detected")
                shutil.move(despath + '/' + tmplist[8][0:4] + '/' + name, "./ERROR_Detected/" + name)
                logger.error(name + " : CRC Failed")
            return False
        pass
    except Exception as e:
        print(e)
        pass
#=================FUNCTION FOR CRC================================
def initCRC_Return_1sCompliment(filename):
    file = open(filename)
    data = ''.join(format(ord(i), '08b') for i in file.read())
    chunks, chunk_size = len(data), len(data)//4
    new_data = [data[i:i+chunk_size] for i in range(0, chunks, chunk_size)]    
    one_com = CRCChecking(new_data)
    file.close()
    return one_com

def initCRC_Return_True(filename,listofonecom):
    file = open(filename)
    data = ''.join(format(ord(i), '08b') for i in file.read())
    #print(data)
    chunks, chunk_size = len(data), len(data)//4
    new_data = [data[i:i+chunk_size] for i in range(0, chunks, chunk_size)]
    
    result = CRCChecking2(new_data, listofonecom)
    #print(result)
    return result

    

def CRCChecking(data):
    
    a = data[0]
    b = data[1]
    c = data[2]
    d = data[3]
    max_len = max(len(a), len(b))
    max_len2 = max(len(c), len(d))
    a = a.zfill(max_len)
    b = b.zfill(max_len)
    c = c.zfill(max_len2)
    d = d.zfill(max_len2)
      
    # Initialize the result
    result = ''
    result2 = ''
      
    # Initialize the carry
    carry = 0
    carry2 = 0
      
    # Traverse the string
    for i in range(max_len - 1, -1, -1):
        r = carry
        r += 1 if a[i] == '1' else 0
        r += 1 if b[i] == '1' else 0
        result = ('1' if r % 2 == 1 else '0') + result
      
        # Compute the carry.
        carry = 0 if r < 2 else 1
      
    if carry != 0:
        result = '1' + result
    # ==========3&4===============    
    for i in range(max_len2 - 1, -1, -1):
        r = carry
        r += 1 if c[i] == '1' else 0
        r += 1 if d[i] == '1' else 0
        result2 = ('1' if r % 2 == 1 else '0') + result2
      
        # Compute the carry.
        carry2 = 0 if r < 2 else 1
      
    if carry2 != 0:
        result2 = '1' + result2
          
    # print(result.zfill(max_len))
    # print("===================================")
    # print(result2.zfill(max_len))
    # print("===================================")
    a1 = result.zfill(max_len)
    b1 = result2.zfill(max_len2)
    max_len1 = max(len(a1), len(b1))
    a1 = a1.zfill(max_len1)
    b1 = b1.zfill(max_len1)
      
    # Initialize the result
    result3 = ''
      
    # Initialize the carry
    carry = 0
      
    # Traverse the string
    for i in range(max_len1 - 1, -1, -1):
        r = carry
        r += 1 if a1[i] == '1' else 0
        r += 1 if b1[i] == '1' else 0
        result3 = ('1' if r % 2 == 1 else '0') + result3
      
        # Compute the carry.
        carry = 0 if r < 2 else 1
      
    if carry != 0:
        result3 = '1' + result3
      
    # print("Before : ")    
    # print(result3.zfill(max_len1))
    checksum = result3.zfill(max_len1).replace('0','D')
    checksum = checksum.replace('1','A')
    final = checksum.replace('A','0')
    final = final.replace('D','1')
    # print("After : ")
    # print(final)
    # print("===========================ASDSD====================")
    a2 = result3.zfill(max_len1)
    b2 = final.zfill(max_len1)
    max_len2 = max(len(a2), len(b2))
    a2 = a2.zfill(max_len2)
    b2 = b2.zfill(max_len2)
      
    # Initialize the result
    result4 = ''
      
    # Initialize the carry
    carry = 0
      
    # Traverse the string
    for i in range(max_len2 - 1, -1, -1):
        r = carry
        r += 1 if a2[i] == '1' else 0
        r += 1 if b2[i] == '1' else 0
        result4 = ('1' if r % 2 == 1 else '0') + result4
      
        # Compute the carry.
        carry = 0 if r < 2 else 1
      
    if carry != 0:
        result4 = '1' + result4
    #print(result4)
   
    
    return final

def CRCChecking2(data,data2):
    a = data[0]
    b = data[1]
    c = data[2]
    d = data[3]
    
    max_len = max(len(a), len(b))
    max_len2 = max(len(c), len(d))
    a = a.zfill(max_len)
    b = b.zfill(max_len)
    c = c.zfill(max_len2)
    d = d.zfill(max_len2)
      
    # Initialize the result
    result = ''
    result2 = ''
      
    # Initialize the carry
    carry = 0
    carry2 = 0
      
    # Traverse the string
    for i in range(max_len - 1, -1, -1):
        r = carry
        r += 1 if a[i] == '1' else 0
        r += 1 if b[i] == '1' else 0
        result = ('1' if r % 2 == 1 else '0') + result
      
        # Compute the carry.
        carry = 0 if r < 2 else 1
      
    if carry != 0:
        result = '1' + result
    # ==========3&4===============    
    for i in range(max_len2 - 1, -1, -1):
        r = carry
        r += 1 if c[i] == '1' else 0
        r += 1 if d[i] == '1' else 0
        result2 = ('1' if r % 2 == 1 else '0') + result2
      
        # Compute the carry.
        carry2 = 0 if r < 2 else 1
      
    if carry2 != 0:
        result2 = '1' + result2
          
    # print(result.zfill(max_len))
    # print("===================================")
    # print(result2.zfill(max_len))
    # print("===================================")
    a1 = result.zfill(max_len)
    b1 = result2.zfill(max_len2)
    max_len1 = max(len(a1), len(b1))
    a1 = a1.zfill(max_len1)
    b1 = b1.zfill(max_len1)
      
    # Initialize the result
    result3 = ''
      
    # Initialize the carry
    carry = 0
      
    # Traverse the string
    for i in range(max_len1 - 1, -1, -1):
        r = carry
        r += 1 if a1[i] == '1' else 0
        r += 1 if b1[i] == '1' else 0
        result3 = ('1' if r % 2 == 1 else '0') + result3
      
        # Compute the carry.
        carry = 0 if r < 2 else 1
      
    if carry != 0:
        result3 = '1' + result3  
        
    a2 = result3.zfill(max_len1)
    b2 = data2.zfill(max_len1)
    max_len2 = max(len(a2), len(b2))
    a2 = a2.zfill(max_len2)
    b2 = b2.zfill(max_len2)
      
    # Initialize the result
    result4 = ''
      
    # Initialize the carry
    carry = 0
      
    # Traverse the string
    for i in range(max_len2 - 1, -1, -1):
        r = carry
        r += 1 if a2[i] == '1' else 0
        r += 1 if b2[i] == '1' else 0
        result4 = ('1' if r % 2 == 1 else '0') + result4
      
        # Compute the carry.
        carry = 0 if r < 2 else 1
      
    if carry != 0:
        result4 = '1' + result4  
        
        
    
    if('0' in result4):
        return False
    else:
        #print(result4)
        return True
#===================FUNCTION FOR CRC==========================================    
#==============Change Path Here================================
path = 'C:\Internship\ProjectNameChanging\CosmoSkymed Data'
new_path = 'C:\Internship\ProjectNameChanging\CosmoSkymed Data'
log_path = 'C:\Internship\ProjectNameChanging\Log_COSMO'
#==============================================================
path = os.path.abspath(path)
new_path = os.path.abspath(new_path)
log_path = os.path.abspath(log_path)

start(path,new_path,log_path)

handlers = logger.handlers[:]
for handler in handlers:
    logger.removeHandler(handler)
    handler.close()