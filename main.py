from fastapi import FastAPI,Path , HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
import json


app=FastAPI()

#pydantic moadel hai jo create kiya hai humne
class Patient(BaseModel):

    id:Annotated[str,Field(...,description="id of the patient")]
    name:Annotated[str,Field(...,description="name of the patient")]
    age:Annotated[int,Field(...,description="age of the patient", gt=0)]
    gender:Annotated[Literal['male','female','others'],Field(...,description="gender of the patient")]
    city:Annotated[str,Field(...,description="city of the patient")]
    height:Annotated[float,Field(...,gt=0,description="heightvof the patient")]
    weight:Annotated[float,Field(...,gt=0,description="weight of the patient")]

   
    @computed_field
    @property
    def bmi(self)->float:

        bmi =round(seld.weght/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self)->str:

        if self.bmi<18.5:
            return 'Underweight'

        elif self.bmi < 25:
            return 'Normal'

        elif self.bmi<30:
            return 'Normal'

        else:
            return "Obese"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]



def load_data():

    with open("patient.json","r")as f:
        data=json.load(f)

    return data


def save_data(data):
    with open("patient.json","w") as f:
        json.dump(data,f)


@app.get("/")
def hello():
    return {"message":"Patient management system"}

@app.get("/about")
def about():
    return{"message":"a fully functional api for managing patients review"}


@app.get("/view")
def view():
    data=load_data()

    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id:str=Path(...,description="id of the patient",example="P001")):

    data=load_data()

    if patient_id in data:
        return data[patient_id]

    raise HTTPException(status_code=404 , detail="patient not found")


@app.get("/sort")
def sort_patient(sort_by:str=Query(...,description="sort on the basis of height,weight or bmi"),order:str=Query(...,description='sort in asc or desc order')):

    valid_fields=['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=404,detail=f"Invalid field select from {valid_fields}")

    if order not in ['asc','desc']:
        raise HTTPException(status_code=404,detail="invalid order select between asc or desc")

    data=load_data()

    sort_order = True if order=='desc' else False

    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)

    return sorted_data


@app.post('/create')
def create_patient(patient:Patient):

    data=load_data()

    if patient.id in data:
        raise HTTPException(status_code=400,detail="patient not found")

    #new patient add
    data[patient.id]=patient.model_dump(exclude=['id'])

    #save into the json file
    save_data(data)

    return JSONResponse(status_code=201, content={"message":"patient updated successfully"})

@app.put("/edit/{patient_id}")
def update_patient(patient_id:str,update_patient:PatientUpdate):

    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail="patient not found")

    existing_patient_info=data[patient_id]

    updated_patient_info=patient_update.model_dump(exclude_unset=True)

    for key,value in updated_patient_info.items():
        existing_patient_info[key]=value


    existing_patient_info['id']=patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)

    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')

    data[patient_id]=existing_patient_info

    save_data(data)

    return JSONResponse(status_code=200,content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):

    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail='patient not found')

    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={'messsage':"patient deleted"})

    