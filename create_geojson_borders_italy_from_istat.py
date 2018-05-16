import geopandas as gpd
import pandas as pd
import numpy as np
import requests, zipfile, io, os
import shutil
zip_file_url='http://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/Limiti01012018_g.zip'
maindir='Limiti01012018_g' 
r = requests.get(zip_file_url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()
dirs = os.listdir(maindir)
heads = ['rip','reg','prov','com']
def getDir(dirs,head):
    rname = None
    for name in dirs:
        if name.lower().startswith(head):
            rname = name
            break
    return rname
# regioni
dirRegion = getDir(dirs,'reg')
regions = os.listdir(os.path.join(maindir,dirRegion))

shp_region = None
for region in regions:
    if region.rfind("shp") > -1:
        shp_region = region
        break
regioni = gpd.read_file(os.path.join(maindir,dirRegion,shp_region))
regioni = regioni[["COD_REG","DEN_REG","geometry"]]
regioni = regioni.rename(index=str, columns={'COD_REG': 'id', 'DEN_REG': 'name','geometry':'geometry'})
regioni = regioni.to_crs({'init': 'epsg:4326'})
# province
dirProvince = getDir(dirs,'prov')
provinces = os.listdir(os.path.join(maindir,dirProvince))

shp_province = None
for province in provinces:
    if province.rfind("shp") > -1:
        shp_province = province
        break
province = gpd.read_file(os.path.join(maindir,dirProvince,shp_province))
province.loc[(province['DEN_PROV'] == "-") & (province['DEN_PCM'] != '-'), ['DEN_PROV']] = province['DEN_PCM']
province = province[["COD_REG","COD_PROV","DEN_PROV","SIGLA","geometry"]]
province = province.rename(index=str, columns={'COD_PROV':'id','COD_REG': 'id_reg', 'DEN_REG': 'name_region','DEN_PROV':'name','SIGLA':'sigla','geometry':'geometry'})
province = province.to_crs({'init': 'epsg:4326'})
# comuni
dirComuni = getDir(dirs,'com')
comuni = os.listdir(os.path.join(maindir,dirComuni))
shp_comuni = None
for comune in comuni:
    if comune.rfind("shp") > -1:
        shp_comuni = comune
        break
comuni = gpd.read_file(os.path.join(maindir,dirComuni,shp_comuni))
comuni = comuni[["COD_REG","COD_PROV","PRO_COM","COMUNE","geometry"]]
comuni = comuni.rename(index=str, columns={'COD_PROV':'id_prov','COD_REG': 'id_reg', 'PRO_COM': 'id','COMUNE':'name','geometry':'geometry'})
comuni = comuni.to_crs({'init': 'epsg:4326'})

# crea directory data
if os.path.exists('geojson'):
    shutil.rmtree("geojson")
os.makedirs("geojson")
filename="regions.json"
regioni.to_file(os.path.join("geojson",filename), driver="GeoJSON")

# crea province e comuni
for id_reg in regioni.id:
    regprov = os.path.join("geojson",str(id_reg))
    os.makedirs(regprov)
    provincia = province[province.id_reg == id_reg]
    fileprovinces = os.path.join(regprov,"provinces.json")
    print(fileprovinces)
    provincia.to_file(fileprovinces, driver="GeoJSON")
    for id_prov in provincia.id:
        provcom = os.path.join("geojson",str(id_reg),str(id_prov))
        filemuncipalities = os.path.join(provcom,"muncipalities.json")
        print(filemuncipalities)
        os.makedirs(provcom)
        comune = comuni[(comuni.id_prov == id_prov) & (comuni.id_reg == id_reg)]
        comune.to_file(filemuncipalities, driver="GeoJSON")
shutil.rmtree(maindir)
