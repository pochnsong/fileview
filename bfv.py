#!/usr/bin/env python
#coding=utf8

import os;
import sys;
import re;
import time;
from math import *;
import function;
#----------------------------------------------------
#----------------------------------------------------
global FV_SWITCH_LIST,FV_ARY,FV_FILE_SIZE,FV_X_COUNT;
FV_SWITCH_LIST=[];
FV_ARY="dec";
FV_FILE_SIZE=0;
FV_X_COUNT=0;
# FV_FILE_LEN 文件总长度 
# FV_FILE_LEN 当前文件指针
global FV_TXT_LOAD;
FV_TXT_LOAD=False;
global FV_TXT_LEN,FV_TXT_I;
FV_TXT_LEN=0;
FV_TXT_I=0;
global FV_TXT;
FV_TXT="";
global FV_TXT_CLOSED;
FV_TXT_CLOSED=False;
#全局函数表
global FV_FUNCTION_LIST;
FV_RUNCTION_LIST=[];
#----------------------------------------------------
def version():
    print "版本：1.0 FVL 原型机";
#----------------------------------------------------
def info():
    try:
        _hpname=sys.path[0]+"/help/help.fileview";
        fi=file(_hpname,"r");
    except:
        print "错误：未找到帮助文件！";
        return;

    text=fi.readlines();
    fi.close();
    for i in text:
        print i,
#------------------------------------------
def get_error_info(err):
    return "错误ID: "+str(err[0])+" 错误内容: "+err[1];
#------------------------------------------
def _uint_n(cn,mod):
    n=len(cn);
    res=0;

    if mod=="a":
        for i in range(n):
            res=res|(ord(cn[i])<<((n-1-i)*8));
    else:
        for i in range(n):
            res=res|( ord(cn[i])<<(i*8) );

    return res;
#------------------------------------------
def _int_n(cn,mod):
    n=len(cn);
    res=_uint_n(cn,mod);
    flag=128<<((n-1)*8);
    
    if flag&res:
        flag=2**(n*8)-1;
        res=-((res^flag)+1);
    
    return res;
#------------------------------------------
def _script_str_(_str_):
    if type(_str_)!=str:
        return "",(1001,"bug! _script_str_ type_error:"+type(_str_));
    res="";
    i=0;
    while i<len(_str_):
        _c=_str_[i];
        if _c=="(" or _c==")" or _c==":":
            res+=" "+_c+" ";
        elif _c=="=" or "["==_c or "]"==_c:
            res+=" "+_c+" ";
        elif "{"==_c or "}"==_c:
            res+=" "+_c+" ";
        elif "@"==_c:
            res+=" "+_c;
        elif "&"==_c:
            res+=" "+_c;
        elif ";"==_c:
            res+=" ";
        elif "\""==_c:
            j=i+1;
            _str_t=" \" ";
            while j<len(_str_):
                _t=_str_[j];
                i=j;
                if _t=="\"":
                    _str_t+="\" ";
                    break;
                else:
                    _str_t=_str_t+str(ord(_t))+" ";
                j+=1;
            res+=_str_t;
        elif "#"==_c:
            j=i+1;
            while j<len(_str_):
                _c=_str_[j];
                if _c=="\n":
                    break;
                j+=1;
                i=j;

        else:
            res+=_c;
        i=i+1;
    res=res.split();
    return res,(0,"");
#------------------------------------------
def _script_get_n_exp_(_str_):
#获取表达式
    if type(_str_)!=list:
        return "",(1001,"bug! _script_get_n_exp_ type error:"+type(_str_));

    res="";
    while len(_str_):
        _c=_str_[0];
        del _str_[0];
        if "]"==_c:
            return res,(0,"");
        else:
            res+=_c;
    return "",(2001,"错误！缺少和 [ 匹配的 ] "+res);
#------------------------------------------
def _script_get_n_(_str_):
    if type(_str_)!=list:
        return 0,(1001,"bug! _script_get_n_ type error:"+type(_str_));
    _n=1;
    if len(_str_)>1 and _str_[0]==":":
        try:
            _n=int(_str_[1]);
        except:
            if _str_[1]=="*":
                del _str_[0];
                del _str_[0];
                return "*",(0,"");
            elif _str_[1]=="[":
                del _str_[0];
                del _str_[0];
                res,err=_script_get_n_exp_(_str_);
                if err[0]:
                    return "",err;
                else:
                    return res,(0,"");
            return "",(2002,"变量错误!错误的循环变量:"+_str_[1]);
        
        del _str_[0];
        del _str_[0];
        if _n<0:
            return "",(2003,"错误的循环变量取值 <0 :"+str(_n));
        
    return _n,(0,"");

#------------------------------------------
def _script_get_format_(_str_):
    if type(_str_)!=list:
        return "",(1001,"bug! _script_get_format_ type error:"+type(_str_))

    res=":";
    while len(_str_):
        _c=_str_[0];
        del _str_[0];
        
        if "\""==_c:
            if len(res)==1:
                res="?";
            return res,(0,"");
        elif "\\"==chr(int(_c)):
            if len(_str_):
                _t=chr(int(_str_[0]));
                del _str_[0];
                if _t=="n":
                    res+="\n";
                elif _t=="t":
                    res+="\t";
                elif _t=="r":
                    res+="\r";
                else:
                    res+=_t;
            else:
                return "",(2004,"无法找到匹配的 \\");
            continue;
        else:
            res+=chr(int(_c));

    return "",(2005,'字符串错误！缺少匹配的 " ',res);
#------------------------------------------
def _id_(_str):
    if type(_str)!=str:
        return False,(1001,"bug! _id_ type error:"+type(_str));
    _ID=re.compile("[$][A-Za-z]([A-Za-z_]|[0-9])*");
    res=_ID.match(_str);
    if res and (0,len(_str))==res.span():
        return True;
    else:
        return False;
#------------------------------------------
def _script_get_id_(_str_):
    if type(_str_)!=list:
        return "",(1001,"bug! _script_get_id_ type error:"+type(_str_))
    if len(_str_)<2:
        return "",(0,"");
    try:
        _c=_str_[0];
        _id=_str_[1];
    except:
        return "",(2006,"变量错误！错误的变量定义!"+_c);
    if _c!="=":
        return "",(0,"");
    else:
        if _id_(_id):
            del _str_[0];
            del _str_[0];
            return _id,(0,"");
        else:
            return "",(2007,"变量错误！不合法的变量定义 "+_id);
#------------------------------------------
def _script_get_exp_(_str_):
#获取表达式
    if type(_str_)!=list:
        return "",(1001,"bug! _script_get_exp_ type error:"+type(_str_));
    res="";
    while len(_str_):
        _c=_str_[0];
        del _str_[0];
        if "]"==_c:
            return res,(0,"");
        elif "\""==_c:
            _res,err=_script_get_format_(_str_);
            if err[0]:
                return "",err;
            elif _res=="?":
                continue;
            else:
                res+='"'+_res[1:]+'"';
        else:
            res+=_c;
    return "",(2008,"表达式错误！无法匹配 [ "+res);

#------------------------------------------
def _key_(_str):
    if type(_str)!=str:
        return False,(1001,"bug! _key_ type error:"+type(_str_))
    _ID=re.compile("[@][A-Za-z_]([A-Za-z_]|[0-9])*");
    res=_ID.match(_str);
    if res and (0,len(_str))==res.span():
        return True,(0,"");
    else:
        return False,(0,"");
#------------------------------------------
def _keyfunction(_str):
    if type(_str)!=str:
        return False,(1001,"bug! _key_ type error:"+type(_str_))
    _ID=re.compile("[&][A-Za-z_]([A-Za-z_]|[0-9])*");
    res=_ID.match(_str);
    if res and (0,len(_str))==res.span():
        return True,(0,"");
    else:
        return False,(0,"");
#------------------------------------------
def _switch_case_(_str_):
#_str_:list
#return (value,[list])
#100
    if type(_str_)!=list:
        return "",(1001,"bug! _switch_case_ type error:"+type(_str_))
    
    _value,err=_script_get_exp_(_str_);
    if err[0]:
        return (),err;
    try:
        _c=_str_[0];
        del _str_[0];
    except:
        return (),(2009,"switch case 错误！ 缺少case定义");

    if ":"!=_c:
        return (),(2010,"switch case 错误！无效的声明运算符："+_c);
    try:
        _c=_str_[0];
        del _str_[0];
    except:
        return (),(2012,"switch case 错误！缺少 {");
    if "{"!=_c:
        return (),(2013,"switch case 错误！非 { :"+_c);
    _list=[];

    while len(_str_):
        _c=_str_[0];
        del _str_[0];
        
        if "}"==_c:
            _res,err=_script_list_(_list);
            
            if err[0]:
                return (),err;
            else:
                return (_value,_res),(0,"");
        else:
            _list.append(_c);
        
    
    #错误！
    return (),(2014,"switch case 错误！未找到匹配的 {"); 
#------------------------------------------
def _switch_default_(_str_):
#_str_:list
#return (value,[list])
#200
    if type(_str_)!=list:
        return "",(1001,"bug! _switch_default_ type error:"+type(_str_))

    try:
        _c=_str_[0];
        del _str_[0];
    except:
        return (),(2015,"错误！switch default");
    if ":"!=_c:
        return (),(2016,_c);
    try:
        _c=_str_[0];
        del _str_[0];
    except:
        return (),(2017,"错误！switch default");
    if "{"!=_c:
        return (),(2018,"错误！switch default "+_c);
    _list=[];
    
    while len(_str_):
        _c=_str_[0];
        del _str_[0];
        
        if "}"==_c:
            _res,err=_script_list_(_list);
            
            if err[0]:
                return (),err;
            else:
                return ("default:",_res),(0,"");
                
        else:
            _list.append(_c);
        
    
    #错误！
    return (),(2019,"switch default 错误！未找到匹配的 {"); 

#------------------------------------------
def _switch_(_str_):
#获取switch{}
#100
    if type(_str_)!=list:
        return "",(1001,"bug! _switch_ type error:"+type(_str_));
    _list=[];
    try:
        _key=_str_[0];
        del _str_[0];
    except:
        return "",(2020,"_switch_");

    res,err=_key_(_key);
    if err[0]:
        return "",err[0];
    if res==False:
        return "",(1,"switch 定义错误！非法的定义"+_key)
    
    _i=0;
    while len(_str_):
        _c=_str_[0];
        del _str_[0];
        if "{"==_c:
            _i+=1;
            continue;
        elif "}"==_c:
            _i-=1;
            if _i==0:
                _script_set_switch_list_((_key,_list));
                return "",(0,"");
            elif _i<0:
                return "",(2021,"switch } 错误！");
            else:
                continue;
        elif "["==_c:
           _res,err=_switch_case_(_str_);
           if err[0]:
               return "",err;
           else:
               _list.append(_res);
        elif "default"==_c:
            _res,err=_switch_default_(_str_);
            if err[0]:
                return "",err
            else:
                _list.append(_res);
        else:
            return "",(2100,"switch case 过程错误！错误的 case 定义:"+_c);

    return _str_,(2022,"switch 错误！");
#------------------------------------------
#------------------------------------------
#------------------------------------------
def _script_get_switch_(_str_):
#获取{}
#5000
    if type(_str_)!=list:
        return "",(1001,"bug! _script_get_switch_ type error:"+type(_str_))
    while len(_str_):
        _c=_str_[0];
        del _str_[0];

        if _c=="switch":
            tmp,err=_switch_(_str_);
            if err[0]:
                return "",err;
            else:
                continue;
        elif "{"==_c:
            tmp,err=_script_get_switch_(_str_);
            if err[0]:
                return "",err;
            else:
                continue;
        elif "}"==_c:
            return "",(0,"");
        else:
            return "",(2101,"过程错误！无效的过程定义:"+_c);
    return "",(2023,"过程错误！无法找的匹配的 { ");
#------------------------------------------
def _script_keyword_base_(_str):
    if type(_str)!=str:
        return False;
    _ID=re.compile("((uint|int)_[0-9]+_[az])|(char_[0-9]+_[az])|(byte)");
    res=_ID.match(_str);
    if res and (0,len(_str))==res.span():
        return True; 
    else:
        return False;

#------------------------------------------
#------------------------------------------
#------------------------------------------
def _script_get_function_parameter_(_str_):
    res=[];
    _c=_str_[0];
    del _str_[0];
    if _c!="(":
        return "",(11001,"函数缺少 ( ");
    _num=1;
    while True:
        _c=_str_[0];
        del _str_[0];

        if _c=="(":
            _num+=1;
        elif _c==")":
            _num-=1;
        if _num==0:
            return res,(0,"");
        elif len(_str_)==0:
            return [],(11002,"缺少 )");
        res.append(_c);
    return res,(11003,"未知错误！ _script_get_function_parameter_");
#------------------------------------------
def _script_list_(_str_):
    if type(_str_)!=list:
        return [],(1001,"bug! _script_list_ type error:"+type(_str_))

    res=[];

    _keyary=['dec','DEC','hex','HEX','bin','BIN']
    if len(_str_)==0:
        return res,(0,"NULL");

    while len(_str_):
        _c=_str_[0];
        del _str_[0];
        
        if _c in _keyary:
            res.append((9,_c));
            continue;
        if "$pos"==_c:
            res.append((20,"$pos"));
            continue;
        elif "int"==_c:
            _c="int_1_a";
        elif "uint"==_c:
            _c="uint_1_a";
        elif "char"==_c:
            _c="char_1_a";
        elif "wchar_t"==_c:
            _c="char_4_a";
        
        if "{"==_c:
            _res,err=_script_get_switch_(_str_);
            if err[0]:
                return [],err;
            continue;
        elif "("==_c:
            _n=1;
            _res,err=_script_list_(_str_);
            if err[0]:
                return [],err;

            _n,err=_script_get_n_(_str_);
            if err[0]:
                return [],err;

            res.append((7,_res,_n));
            continue;

        elif ")"==_c:
            return res,(0,"");
        elif _script_keyword_base_(_c):
            #base_n_z 
            _n,err=_script_get_n_(_str_);
            if err[0]:
                print _c;
                return [],err;

            _res,err=_script_get_id_(_str_);
            if err[0]:
                return [],err;

            if "byte"==_c:
                res.append((4,_n));
                continue;
            _tmp=_c.split("_");
            if "char"==_tmp[0]:
                _base=(1,int(_tmp[1]),_tmp[2]);
                _id_type=1;
            elif "int"==_tmp[0]:
                _base=(2,int(_tmp[1]),_tmp[2]);
                _id_type=2;
            else:
                _base=(3,int(_tmp[1]),_tmp[2]);
                _id_type=3;
            if not _res:                          
                if _n==1:
                    res.append(_base);          
                else:
                    res.append((7,[_base],_n));
                continue;
            else:
                if _n>1:
                    _id_type=1;
                res.append((8,_res,_id_type,(7,[_base,(6,0)],_n))); 
            continue;
        elif "\""==_c:
            _res,err=_script_get_format_(_str_);
            if err[0]:
                return [],err;
            if _res=="?":
                res.append((6,0));
            else:
                res.append((5,_res[1:]));
            continue;

        _res,err=_key_(_c);
        if err[0]:
            return [],err;
        elif _res:
            
            if _script_find_switch_list_(_c)==False:
                return res,(2024,"过程调用错误！试图使用未定义的过程:"+_c);
            try:
                _c1=_str_[0];
                _c2=_str_[1];
                del _str_[0];
                del _str_[0];
                
            except:
                return res,(2025,"过程调用错误！"+_c);
            if _c1!="(" or _c2!="[":
                return res,(2026,"过程调用错误！"+_c);
            else:
                _res,err=_script_get_exp_(_str_);
                if err[0]:
                    return [],err;
                try:
                    _c1=_str_[0];
                    del _str_[0];
                except:
                    return res,(2027,"过程缺少结束符 ） "+_c);
            if not _res or _c1!=")":
                return res,(2028,"错误!不正确的的过程结束符 "+_c+":"+_c1);
            else:
                res.append((10,_c,_res));
            continue;
#!@#
        _res,err=_keyfunction(_c);
        if err[0]:
            return [],err;
        elif _res:
            _fnname=_c;
            _para,err=_script_get_function_parameter_(_str_);
            if err[0]:
                return [],err;
           
            _fn_list,err=_script_list_(_para);
            if err[0]:
                return [],err;
            res.append((11,_fnname,_fn_list));
        else:
            return res,(2029,"关键字错误！当前版本无法识别的表示符:"+_c);
                    
    return res,(0,"");

#------------------------------------------
def _script_define_id_(_id,_value):
    _id=_id.replace("$","__fileview_")
    _str="global "+_id+";"+_id+"="+_value;
    exec(_str);

#------------------------------------------
def _script_eval_(_str):
    if type(_str)!=str:
        return "",(1001,"bug! _script_eval_ type error:"+type(_str));
    _tmp=_str.replace("$","__fileview_")
    res=0;
    try :
        res=int(eval(_tmp));
    except:
        return 0,(2030,"表达式错误！表达式"+_str+" 格式错误，或者未定义！");
    if res<0:
        return 0,(2031,"表达式错误！无法产生非负值的表达式:"+_str+":"+res)
    return res,(0,"");
#------------------------------------------
def _script_set_switch_list_(_key):
    i=0;
    while i<len(FV_SWITCH_LIST):
        _l=FV_SWITCH_LIST[i];
        if _l[0]==_key[0]:
            del FV_SWITCH_LIST[0];
            break;
        else:
            i+=1;
    
    FV_SWITCH_LIST.append(_key);
                        
#------------------------------------------
def _script_find_switch_list_(_key):

    for i in FV_SWITCH_LIST:
        if i[0]==_key:
            return True;
    return False;
#------------------------------------------
def _script_get_switch_list_x_(_key,_value):
    try:
        _res2=_value.replace("$","__fileview_");
        _res2=eval(_res2);
    except:
        return "",(2032,"错误的 @过程 参数:"+_value)
    
    res="";
    for i in FV_SWITCH_LIST:
        if i[0]==_key:
            for j in i[1]:
                if j[0]=="default:":
                    res=j[1];
                    
                else:
                    
                    try:  
                        _res1=j[0].replace("$","__fileview_");
                        _res1=eval(_res1);
                    except Exception,e:
                        #print _res1;
                        #eval(_res1);
                        return "",(2033,_key+" switch case 错误的表达:"+j[0]+":"+str(e));
                    if _res1==_res2:
                        return j[1],(0,"");
                
            break;
    return res,(0,"");
#------------------------------------------
def _ary_(_str):
    if FV_ARY=="hex":
        return "%x"%_str;
    elif FV_ARY=="HEX":
        return "%X"%_str;
    elif FV_ARY=="bin" or FV_ARY=="BIN":
        return bin(_str);
    else:
        return str(_str);

#------------------------------------------
#------------------------------------------
def _script_function_(_fnname,_para):
    res="";
    _fnname=_fnname.replace("&","function.");
    tmp=_fnname+"(_para)";
   
    try:
        res=eval(tmp);
    except Exception,e:
        return "",(11009,"function 错误！"+tmp+":"+str(e));
    
    return res,(0,"");

#------------------------------------------
def _script_run_x_(fi,_list_):

    global FV_ARY;

    if fi.closed:
        return "",(1,"close")

    res="";
    _keyary=['dec','DEC','hex','HEX','bin','BIN']
    _e=0;
    i=0;
    _t="";
    print "\r 总计：",FV_FILE_SIZE,"当前：",fi.tell(),

    while i<len(_list_) :
        _c=_list_[i];
        i=i+1;
        _id="";
        if _c[0]==8:
            #id
            _id=_c[1];
            _type=_c[2];
            _c=_c[3];
            _res,err=_script_run_x_(fi,[_c]);
            if err[0]:
                break;
            res+=_res;
            
            if _type==1:
                _script_define_id_(_id,'"'+_res+'"');
            else:
                if FV_ARY=="hex" or FV_ARY=="HEX":
                    _script_define_id_(_id,"0x"+_res);
                else:
                    _script_define_id_(_id,_res);
            continue;
        elif _c[0]==4:
            #byte
            _n=_c[1];
            if type(_n)==str:
                _n,err=_script_eval_(_n);
                if err[0]:
                    return "",err;
             
            fi.seek(fi.tell()+_n);
            continue;
        elif _c[0]==20:
            #$pos
            res+=str(fi.tell());
            _exp="global __fileview_;__fileview_pos="+str(fi.tell())+";";
            try:
                exec(_exp);
            except Exception,e:
                return "",(20001,_exp+":"+str(e));
            continue;

        if _c[0]==7:
            #[.....],n
            res+=_t;
            if _c[2]=="*":
                _I_=0;
                while True:
                    _res,err=_script_run_x_(fi,_c[1]);
                    res+=_res;
                    _I_+=1;
                    if err[0]:
                        res+="\n*="+str(_I_);
                        global FV_X_COUNT;
                        FV_X_COUNT=_I_;
                        return res,err;
                continue;
            else:
                if type(_c[2])==str:
                    N,err=_script_eval_(_c[2]);
                    if err[0]:
                        return "",err;
                else:
                    N=_c[2];
            
                for j in range(N):
                    _res,err=_script_run_x_(fi,_c[1]);
                    if err[0]:
                        return res,err;
                    res+=_res;
                continue;
        elif _c[0]==10:
            _key=_c[1];
            _value=_c[2];
            _list_tmp,err=_script_get_switch_list_x_(_key,_value);
            if err[0]:
                return res,err;

            _res,err=_script_run_x_(fi,_list_tmp);
            res+=_res;
            if err[0]:
                return res,err;
            continue;
        elif _c[0]==9:
            FV_ARY=_c[1];
            continue;
        elif _c[0]==5:
            res+=_c[1]
            _t="";
            continue;
        elif _c[0]==6:
            _t="";
            continue;
        elif _c[0]==1 or _c[0]==2 or _c[0]==3:
            
            _n=_c[1]+FV_TXT_I;
            _str="";
            _str=fi.read(_n);
            if _n!=0 and (not _str):
                fi.close();
                res+=_t+"EOF!";
                return res,(1,"eof");
            
            #print len(_str);
            if _c[0]==1:
                if _c[2]=="z":
                    _str=_str[::-1];
                _res=_str;
            elif _c[0]==2:
                _res=_ary_(_int_n(_str,_c[2]));
            else :
                _res=_ary_(_uint_n(_str,_c[2]));
            
            res+=_t+_res;
            _t=" ";
            continue;
        elif _c[0]==11:
            #函数模块
            _res,err=_script_run_x_(fi,_c[2]);
            if err[0]:
                return _res,err;
           
            _res,err=_script_function_(_c[1],_res);
            if err[0]:
                return _res,err;
            
            res+=_t+_res;
        else:
            return res,(3001,"bug! _list_ 错误:"+str(_c));


    return res+_t,(0,"");
#------------------------------------------
def _script_run_txt_(_list_):
    global FV_ARY;
    global FV_TXT_LEN,FV_TXT_I,FV_TXT,FV_TXT_CLOSED;
    if FV_TXT_CLOSED:
        return "",(1,"close"),
    
    res="";
    _keyary=['dec','DEC','hex','HEX','bin','BIN']
    _e=0;
    i=0;
    _t="";
    print "\r 总计：",FV_TXT_LEN,"当前：",FV_TXT_I,
    while i<len(_list_) :
        _c=_list_[i];
        i=i+1;
        _id="";
        if _c[0]==8:
            #id
            _id=_c[1];
            _type=_c[2];
            _c=_c[3];
            _res,err=_script_run_txt_([_c]);
            if err[0]:
                break;
            res+=_res;
            
            if _type==1:
                _script_define_id_(_id,'"'+_res+'"');
            else:
                if FV_ARY=="hex" or FV_ARY=="HEX":
                    _script_define_id_(_id,"0x"+_res);
                else:
                    _script_define_id_(_id,_res);
            continue;
        elif _c[0]==4:
            #byte
            _n=_c[1];
            if type(_n)==str:
                _n,err=_script_eval_(_n);
                if err[0]:
                    return "",err;
            
            FV_TXT_I+=_n;
            continue;

        if _c[0]==7:
            #[.....],n
            res+=_t;
            if _c[2]=="*":
                _I_=0;
                while True:
                    _res,err=_script_run_txt_(_c[1]);
                    res+=_res;
                    _I_+=1;
                    if err[0]:
                        res+="\n*="+str(_I_);
                        global FV_X_COUNT;
                        FV_X_COUNT=_I_;
                        return res,err;
                continue;
            else:
                if type(_c[2])==str:
                    N,err=_script_eval_(_c[2]);
                    if err[0]:
                        return "",err;
                else:
                    N=_c[2];
            
                for j in range(N):
                    _res,err=_script_run_txt_(_c[1]);
                    if err[0]:
                        return res,err;
                    res+=_res;
                continue;
        elif _c[0]==10:
            _key=_c[1];
            _value=_c[2];
            _list_tmp,err=_script_get_switch_list_x_(_key,_value);
            if err[0]:
                return res,err;

            _res,err=_script_run_txt_(_list_tmp);
            res+=_res;
            if err[0]:
                return res,err;
            continue;
        elif _c[0]==9:
            FV_ARY=_c[1];
            continue;
        elif _c[0]==5:
            res+=_c[1]
            _t="";
            continue;
        elif _c[0]==6:
            _t="";
            continue;
        elif _c[0]==1 or _c[0]==2 or _c[0]==3:
            
            _n=_c[1]+FV_TXT_I;
            _str="";
            while FV_TXT_I<_n:
                try:
                    _str+=FV_TXT[FV_TXT_I];
                    FV_TXT_I+=1;
                except:
                    FV_TXT_CLOSED=True;
                    res+=_t+"EOF!";
                    return res,(1,"eof");
            
            #print len(_str);
            if _c[0]==1:
                _res=_str;
            elif _c[0]==2:
                _res=_ary_(_int_n(_str,_c[2]));
            else :
                _res=_ary_(_uint_n(_str,_c[2]));
            
            res+=_t+_res;
            _t=" ";
            continue;

        else:
            return res,(3001,"bug! _list_ 错误:"+_c);
        

    return res+_t,(0,"");

#------------------------------------------
def _script_run_(_file_,_list_):
    try:
        fi=file(_file_,"rb");
    except:
        return "",(2001,"无法打开文件："+_file_);
    if FV_TXT_LOAD:
        print "正在装载文件",_file_;
        global FV_TXT,FV_TXT_LEN,FV_TXT_I;
        FV_TXT=fi.read();
        FV_TXT_LEN=len(FV_TXT);
        FV_TXT_I=0;
        res,err=_script_run_txt_(_list_);
        if err[0]==1:
            return res,(0,"");
        else:
            return res,err;

    else:
        global FV_FILE_SIZE;
        FV_FILE_SIZE=os.stat(_file_).st_size;

        res,err=_script_run_x_(fi,_list_);
        fi.close();
        if err[0]==1:
            return res,(0,"");
        else:
            return res,err;
#----------------------------------------------------
def format_argv(ss):
    _code="";
    _value="";
    i=0;
    while i<len(ss):
        if ss[i]=='=':
            _value=ss[i+1:];
            break;
        _code=_code+ss[i];
        i=i+1;
    return _code,_value;

#------------------------------------------
def main(argc,argv):

    _filename="";
    _script="";
    _coding="utf8";
    _saveas="";
    _V=False;
    _display=True;
    for i in argv[1:]:
        code,value=format_argv(i);
        if code=="--script":
            _script=value;
            continue;
        elif code=="--file":
            _filename=value;
            continue;
        elif code=="--coding":
            _coding=value;
            continue;
        elif code=="--help":
            info();
            return 0;
        elif code=="--version":
            version();
            return 0;
        elif code=="--save":
            _saveas=value;
            continue;
        elif code=="-v":
            _V=True;
            continue;
        elif code=="--load":
            global FV_TXT_LOAD;
            FV_TXT_LOAD=True;
            continue;
        elif code=="--display":
            if "false"==value.lower():
                _display=False;
            elif "true"==value.lower():
                _display=True;
            else:
                print "警告！忽略无效的 --display 值。当前值为",_display;
        else:
            print "警告！忽略无效的参数",code;

    if not _filename:
        print "J.J.D.L. 文件查看工具 \n请使用--help 获取帮助";
        return 0;
    
    if _V:
        print "预处 FVL 文件...";
    time.clock();
    if len(_script):
        try:
            fi=file(_script,"r");
        except:
            print "错误！读取脚本文件:",_script,"错误！";
            return 1;
        txt=fi.read();
        fi.close();
        _str,err=_script_str_(txt);
        if err[0]:
            print err[1];
            return 1;
    else:
        _str="( uint ) : *";
        _str=_str.split();
    if _V:
        print "完成！";
        print "处理 FLV 文件...";

    time_flv_1=time.clock();
    _list_,err=_script_list_(_str);
    
   
    time_flv_2=time.clock();
    if err[0]==0:
        if _V:
            print "完成!";
            print "参照 FLV 读取目标文件...";
            
        res,err=_script_run_(_filename,_list_);
        time_run=time.clock();
        if _V:
            print "完成！";
        
        if err[0]:
            print get_error_info(err);
            return;
        else:
            if _V:
                print "正在处理输出编码...",
            if _coding!="utf8":
                _txt=res.decode(_coding);
                try:
                    _txt=res.decode(_coding);
                except:
                    print "警告！忽略未知的的编码！",_coding;
                    print res;
                    return 0;
                res=_txt.encode("utf8");
            if _V:
                print "完成!";
            time_coding=time.clock();
            print;
            if _display:
                print res;
            if _V:
                print "预处理 FVL 耗时：",time_flv_1;
                print "处理 FVL 文件耗时：",time_flv_2;
                print "运行 FVL 耗时：",time_run;
                print "编码 耗时：",time_coding;

            if not _saveas:
                return 0;
            try:
                fo=file(_saveas,"w");
            except:
                print "错误！无法写入文件",_saveas;
                return 1;
            fo.write(res);
            fo.close();
            print "已经写入到文件",_saveas;
            return 0;
    else:
        print get_error_info(err);
        if _V:
            print "失败!";

    return 0;

#------------------------------------------
main(len(sys.argv),sys.argv);
