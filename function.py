#!/usr/bin/evn python
#coding=utf8
import zlib;
import Image;
import StringIO;
import sys;
#fileview 函数模块
#------------------------------------------
def utf_16_le(_str):
    try:
        res=_str.decode('UTF-16');
        res=res.encode('UTF8');
    except:
        return "";

    return res;

#------------------------------------------
def unicode(_str):
#去除零
    res="";
    for i in range(len(_str)/2):
        if ord(_str[i*2])+ord(_str[i*2+1]):
            res+=_str[i*2]+_str[i*2+1];
    return utf_16_le(res);
#------------------------------------------
def zlib_decompress(_str):
    try:
        res=zlib.decompress(_str);
    except:
        return "";
    return res;
#------------------------------------------
def image(_data):
    try:
        _image=StringIO.StringIO();
        _image.write(_data);
        _image.seek(0);
        Image.open(_image).show();
        
    except Exception,err:
        print err;
        return "image error!";
    return "Image Show!";
#------------------------------------------
