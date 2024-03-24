import json
import pandas as pd
import logging
from flask import Flask, jsonify, request, flash, redirect, Response
from pathlib import Path
import os
from  pdfid_v0_2_8 import pdfid
from  xml.dom import minidom
import xmltodict
import pickle

app = Flask(__name__)

    

    
@app.route("/", methods=["POST"])
def upload():
    
    try:
        print(request)
        pdf_file = request.files["file"]
        pdf_name = pdf_file.filename
        print(pdf_name)
        save_path = os.path.join(pdf_name) 
        pdf_file.save(save_path)
        with open("pdf_checker_RT",'rb') as f:
            model = pickle.load(f)
            
        result = pdfid.PDFiD(pdf_name)
        data_dict = pdfid.PDFiD2JSON(result,True)
        json_dict = json.loads(data_dict)
        print(json_dict[0]["pdfid"]["keywords"]["keyword"])
        data_list = json_dict[0]["pdfid"]["keywords"]["keyword"]
        data_dict_master = {}
        for data in data_list:
            data_dict = {data["name"].replace("/",""):[data["count"]]}
            data_dict_master = data_dict_master | data_dict
        print(data_dict_master)

        df = pd.DataFrame.from_dict(data_dict_master)

        df_filter = df[["Encrypt","stream","obj","startxref","JBIG2Decode","AcroForm","JavaScript","JS","OpenAction","RichMedia","Launch","EmbeddedFile","XFA","AA"]]

        df_filter.rename(columns = {'Encrypt':'encrypt','JavaScript':'Javascript_coded','JBIG2Decode':'JBIG2Decode_coded','AcroForm':'Acroform_coded','obj':'obj_coded','startxref':'startxref_coded','JS':'JS_coded','OpenAction':'OpenAction_coded','RichMedia':'RichMedia_coded','Launch':'launch_coded','EmbeddedFile':'EmbeddedFile_coded','AA':'AA_coded','XFA':'XFA_coded'}, inplace = True) 
        df_filter["encrypt"] = df_filter["encrypt"].astype(float)
        df_filter["stream"] = df_filter["stream"].astype(float)
        df_filter["startxref_coded"] = df_filter["startxref_coded"].astype("int8")
        df_filter["Javascript_coded"] = df_filter["Javascript_coded"].astype("int8")
        df_filter["JS_coded"] = df_filter["JS_coded"].astype("int8")
        df_filter["OpenAction_coded"] = df_filter["OpenAction_coded"].astype("int8")
        df_filter["RichMedia_coded"] = df_filter["RichMedia_coded"].astype("int8")
        df_filter["launch_coded"] = df_filter["launch_coded"].astype("int8")
        df_filter["EmbeddedFile_coded"] = df_filter["EmbeddedFile_coded"].astype("int8")
        df_filter["AA_coded"] = df_filter["AA_coded"].astype("int8")
        df_filter["XFA_coded"] = df_filter["XFA_coded"].astype("int8")
        df_filter["JBIG2Decode_coded"] = df_filter["JBIG2Decode_coded"].astype("int8")
        df_filter["Acroform_coded"] = df_filter["Acroform_coded"].astype("int8")

            
        result = model.predict(df_filter)
        print(str(result[0]))
        if (result[0] == 0):
            return "valid"
        else:
            return "invalid"
            


    except Exception as e:
        print(e)
        app.logger.info("error occurred")
        return "Fail"
if __name__ == "__main__":
    app.run(port="5000")
    
    
    

