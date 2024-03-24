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
import os
from  pdf_parser_V0_7_8 import pdf_parser
import xmltodict
import json
import subprocess


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

            
        result = pdfid.PDFiD(pdf_name)
        data_dict = pdfid.PDFiD2JSON(result,True)
        json_dict = json.loads(data_dict)
        data_list = json_dict[0]["pdfid"]["keywords"]["keyword"]
        data_dict_master = {}
        for data in data_list:
            data_dict = {data["name"].replace("/",""):[data["count"]]}
            data_dict_master = data_dict_master | data_dict
        print(data_dict_master)

        df = pd.DataFrame.from_dict(data_dict_master)

        df_input = df[["Encrypt","stream","obj","ObjStm","startxref","JBIG2Decode","AcroForm","JavaScript","JS","OpenAction","RichMedia","Launch","EmbeddedFile","XFA","AA"]]

        df_input.rename(columns = {'Encrypt':'encrypt','JavaScript':'Javascript','AcroForm':'Acroform','Launch':'launch'}, inplace = True)

        feature_list = ["xref","obj","ObjStm","startxref","JBIG2Decode","Acroform","Javascript","JS","OpenAction","RichMedia","launch","EmbeddedFile","XFA","AA"]


        for feature_name in feature_list:
            test_feature_name = feature_name + "_coded"
        
            with open("Models/" + test_feature_name,'rb') as f:
                model = pickle.load(f)
            try:
                df_input[test_feature_name] = model.transform( [str(df_input[feature_name][0])] )
            except Exception as e:
                list(model.classes_)
                #print(e)
                continue

        df_input_predict = df_input[['encrypt','stream','obj_coded','ObjStm_coded','startxref_coded','JBIG2Decode_coded','Acroform_coded','Javascript_coded', 'JS_coded','OpenAction_coded','RichMedia_coded','launch_coded','EmbeddedFile_coded','XFA_coded','AA_coded']]

        with open("Models/pdf_checker_RT",'rb') as f:
            model = pickle.load(f)
            
        result = model.predict(df_input_predict)
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
    app.run(port="5001")
    
    
    

