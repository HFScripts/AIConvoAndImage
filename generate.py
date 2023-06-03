#!/usr/bin/python
import argparse
import random
import json
import requests
import time
import pprint
import base64

def runQuery(config):
    url = config["url"]
    del config["url"]

    if config["outfile"] == "":
        outfile = "result." + config["output_format"]
    else:
        outfile = config["outfile"]
    del config["outfile"]

    payload = json.dumps(config, indent=3)
    print(payload)

    req = requests.post( url+"/render", data=payload)
    stream = json.loads(req.text)["stream"]
    decoder = json.JSONDecoder()

    while True:
       time.sleep(1)
       req = requests.get(url + stream)
       if req.text != "":
           data = decoder.raw_decode( req.text )[0]
           if "step" in data:
              t = ( data["total_steps"] - data["step"] ) * data["step_time"]
              print("Progress: %d of %d steps completed, %2.1fs left" % (data["step"], data["total_steps"], t))
           if "status" in data:
              if data["status"] == "succeeded":
                  header, encoded = data["output"][0]["data"].split(",",1)
                  data = base64.b64decode(encoded)
                  with open(outfile, "wb") as f:
                      f.write(data)
                  print(" Completed")
              else:
                  print(" Error: " + data["status"])
              return

def parseArguments():
    rnd = random.randrange(4000000000)

    config = {
        "prompt": "Sarah, flirty, elf, mage, blond hair, brown eyes, medium breasts, fair skin, wearing red warrior outfit, happy, Studio Quality, 6k , toa, toaair, 1boy, glowing, axe, mecha, science_fiction, solo, weapon, jungle, green_background, nature, outdoors, solo, tree, weapon, mask, dynamic lighting, detailed shading, digital texture painting",
        "negative_prompt": "",
        "height": "512",
        "width": "512",
        "guidance_scale": "7.5",
        "steps": 25,
        "num_outputs": 1,
        "output_format": "png",
        "render_device": "0",
        "sampler_name": "euler_a",
        "seed": rnd,
        "session_id": "txt2img",
        "turbo": "true",
        "use_full_precision": "false",
        "use_stable_diffusion_model": "revAnimated_v122",
        "use_vae_model": "",
        "save_to_disk_path": "",
        "url": "http://192.168.1.30:9090",
        "outfile": ""  # Add the 'outfile' key with a default value
    }

    return config

config = parseArguments()
runQuery(config)
