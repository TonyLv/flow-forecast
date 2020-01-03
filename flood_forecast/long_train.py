from flood_forecast.trainer import train_function
import json
import re
import uuid
import os

def split_on_letter(s):
    match = re.compile("[^\W\d]").search(s)
    return [s[:match.start()], s[match.start():]]

from flood_forecast.trainer import train_function
import json
def loop_through(data_dir:str, interrmittent_gcs=False, use_transfer=True): 
  """
  Function that makes and executes a set of config files
  This is since we have over 9k files.
  """
  if not os.path.exists("model_save"):
    os.mkdir("model_save")
  for file_name in sorted(os.listdir(data_dir)):
    station_id_gage = file_name.split("_flow.csv")[0]
    res = split_on_letter(station_id_gage)
    gage_id = res[0]
    station_id = res[1]
    file_path_name = os.path.join(data_dir, file_name)
    if use_transfer and len(os.listdir("model_save")) >1 :
      weight_files = filter(lambda x: x.endswith(".pth"), os.listdir("model_save"))
      paths = [] 
      for weight_file in weight_files:
        paths.append(os.path.join("model_save", weight_file)) 
      correct_file = max(paths, key = os.path.getctime)
      print(correct_file)
    config = make_config_file(file_path_name, gage_id, station_id)
    extension = ".json"
    file_name_json = station_id + "config_f"+extension
    with open(file_name_json, "w+") as f:
        json.dump(config, f)
    os.system('python flood_forecast/trainer.py -p ' + file_name_json)
    
def make_config_file(flow_file_path, gage_id, station_id, weight_path=None):
  the_config = {                 
      "model_name": "MultiAttnHeadSimple",
      "model_type": "PyTorch",
      #"weight_path": "31_December_201906_32AM_model.pth",
      "model_params": {
        "number_time_series":3,
        "seq_len":36
      },
      "dataset_params":
      {  "class": "default",
        "training_path": flow_file_path, 
        "validation_path": flow_file_path,
        "test_path": flow_file_path,
        "batch_size":20,
        "forecast_history":36,
        "forecast_length":36,
        "train_end":35000,
        "valid_start":35001,
        "valid_end": 40000,
        "target_col": ["cfs1"],
        "relevant_cols": ["cfs1", "precip", "temp"],
        "scaler": "StandardScaler"
      },
      "training_params":
      {
        "criterion":"MSE",
        "optimizer": "Adam",
        "optim_params":{
            "lr": 0.001
            # Default is lr=0.001
        },
        
        "epochs":14 ,
        "batch_size":20
      
      },
      "GCS": False,
      
      "wandb": {
        "name": "flood_forecast_"+str(gage_id),
        "tags": [gage_id, station_id, "MultiAttnHeadSimple", "36", "corrected"]
      },
      "forward_params":{}
      }
  if weight_path:
    the_config["weight_path"] = weight_path
      #31_December_201906_12AM_model.pth
  return the_config

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Argument parsing for training and eval")
    parser.add_argument("-p", "--path", help="Data path")

if __name__ == "__main__":
    main()