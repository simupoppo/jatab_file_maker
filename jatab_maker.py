import os
import sys
import glob


# read argv
args = sys.argv

# UI function
# on going...
def UI_function():
    where_show=0
    print_function("What is the input file name?",where_show)
    infile_path=input_function()
    print_function("What is the output file name (.tab file)?",where_show)
    outfile_path=input_function()
    return infile_path,outfile_path,where_show




# main: only read args
def main():
    infile_path=[]
    where_show=0
    print_function(str(args),where_show)
    if len(args)>1:
        if( args[1][-4:]!=".pak" ):
            print_function("please input pakfile name",where_show)
        if( args[len(args)-1][-4:]==".tab"):
            print_function("tab file "+args[len(args)-1],where_show)
            for i in range(len(args)-2):
                temp_infile_path=args[i+1]
                print_function("reading:"+temp_infile_path,where_show)
                infile_path+=(glob.glob(temp_infile_path))
            outfile_path=args[len(args)-1]
        else:
            print_function("no tab files",where_show)
            for i in range(len(args)-1):
                temp_infile_path=args[i+1]
                print_function(temp_infile_path,where_show)
                infile_path+=(glob.glob(temp_infile_path))
            outfile_path="ja.allpaks.tab"
    else:
        temp_infile_path,outfile_path,where_show=UI_function()
        infile_path+=glob.glob(temp_infile_path)
    print_function("infiles:"+str(infile_path),where_show)
    for j in range(len(infile_path)):
        print_function("read "+infile_path[j]+" and write "+outfile_path,where_show)
        jatab_maker(infile_path[j],outfile_path,where_show)




# input function

def input_function(input_file="",input_way="",where_show=0):
    if where_show==1:
        input_file=""
    else:
        return input()

        





# print function
def print_function(texts,where_show=0):
    if where_show!=1:
        print(texts+"\n")

def ask_function(texts,answer,where_show=0,output_type=0):
    print_function(texts+"(default:"+str(answer)+")",where_show)
    output=input_function(where_show=where_show)
    # output_type is int_value. output_type==0 means output must be str. output_type==1 means output must be int.
    if output == "":
        print_function("No input. Treated as "+str(answer))
        output=answer
    if output_type==1:
        try:
            return int(output)
        except Exception:
            print_function("input is not int. Trated as "+str(answer))
    else:
        return output

# main_function
def jatab_maker(infile_path,outfile_path,where_show=0):
    obj_with_name_list=[b"BRDG",b"BUIL",b"CCAR",b"GOOD",b"GOBJ",b"SIGN",b"TUNL",b"VHCL",b"WAY\00",b"WYOB"]
    def read_header(infile,outfile):
        # copy file header 
        for i in range(1000):
            temp_data=infile.read(1)
            if not temp_data:
                print_function("Is this a wrong file?",where_show)
                return False
            if temp_data==b"\x1a":
                version_data=infile.read(4)            
                return True
    def read_root(infile,outfile):
        # copy root and read the number of addons in the pakfile
        root = infile.read(4)
        if root!=b"ROOT":
            print_function("Broken file",where_show)
            return False
        nchild_byte = infile.read(2)
        nchild = int.from_bytes(nchild_byte,byteorder="little")
        print_function("Number of addons : "+str(nchild),where_show)
        root_size = infile.read(2)
        if nchild>0:
            read_object(infile,outfile,nchild)
            return True
        else:
            print_function("a number of child is wrong",where_show)
            return False
    def read_object(infile,outfile,root_nchild):
        for i in range(root_nchild):
            obj_type = infile.read(4)
            obj_nchild_byte = infile.read(2)
            obj_size_byte = infile.read(2)
            obj_size=int.from_bytes(obj_size_byte,byteorder="little")
            if obj_size == 0xFFFF:
                obj_size_large_byte = infile.read(4)
                obj_size=int.from_bytes(obj_size_large_byte,byteorder="little")
            obj_nchild = int.from_bytes(obj_nchild_byte,byteorder="little")
            if obj_type in obj_with_name_list:
                infile.read(obj_size)
                outfile.write(read_text(infile))
                outfile.write("\n\n")
                read_object(infile,outfile,obj_nchild-1)                
            else:
                infile.read(obj_size)
                read_object(infile,outfile,obj_nchild)
        return
    def read_text(infile):
        text=infile.read(4)
        text_nchild=infile.read(2)
        text_size_byte=infile.read(2)
        text_size=int.from_bytes(text_size_byte,byteorder="little")
        output=infile.read(text_size-1)
        infile.read(1)
        if text==b"TEXT" and text_nchild==b"\x00\x00":
            return output.decode("ascii",errors='ignore') 
        else:
            return ""       




    samefile_flag=0
    try:
        infile=open(infile_path,"br")
        outfile=open(outfile_path,"a")
    except Exception:
        print_function("No file!",where_show)
        return False
    a=read_header(infile,outfile)
    if not a:
        return False
    print_function("read "+infile_path,where_show)
    outfile.write("#___"+os.path.basename(infile_path)+"___\n")
    outfile.write("#___\n")
    a=read_root(infile,outfile)
    if not a:
        return False
    infile.close()
    outfile.close()
    if a:
        print_function("tab file writing done!",where_show)



if __name__ == "__main__":
    main()