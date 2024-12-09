#!/usr/bin/env python
#IMPORT STD---------------------------------------------------------------------
import os.path
import sys
import time
import shutil
import argparse
import json
from os.path import basename, splitext
from threading import Thread
# importing the requests library 
import urllib.request

# importing configgen library
sys.path.append('/usr/lib/python3.11/site-packages/configgen/settings/')
from configgen.settings.keyValueSettings import keyValueSettings

#CONSTANTS---------------------------------------------------------------------                             
VERSION='1.0.0 09/12/2024'
SOURCE_NAME='BozoTheGeek'
URL_ESP8266_1 = "http://192.168.0.106/"
URL_ESP8266_2 = "http://192.168.0.107/"

SYSTEMS_BUTTONS_MAPPING =\
{
#   SYSTEM            A B X Y R1L1R2L2
#   6 button console    
    'snes'         : [1,1,1,1,1,1,0,0],
    'sega32x'      : [1,1,1,1,1,1,0,0],
    'fba_libretro' : [1,1,1,1,1,1,0,0],
#    'megadrive'    : [1,1,1,1,1,1,0,0],
#   2 buttons console    
    'nes'          : [1,1,0,0,0,0,0,0],
    'mastersystem' : [1,1,0,0,0,0,0,0],
    'pcengine'     : [1,1,0,0,0,0,0,0],
    'atari7800'    : [1,1,0,0,0,0,0,0],
    'atari5200'    : [1,1,0,0,0,0,0,0],
#   1 button console    
    'atari2600'    : [0,1,0,0,0,0,0,0],
#   3 buttons console 
    'megadrive'    : [1,1,0,0,1,0,0,0],
#   4 buttons console 
    'neogeo'       : [1,1,0,0,1,0,1,0],
    'neogeocd'     : [1,1,0,0,1,0,1,0],
    'vectrex'      : [1,1,0,0,1,0,1,0],
#   All buttons
    'mame'         : [1,1,1,1,1,1,1,1],
    'n64'          : [1,1,1,1,1,1,1,1],
    'colecovision' : [1,1,1,1,1,1,1,1],
}

def Log(txt):
    import datetime
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    #uncomment/comment the following line to activate/desactivate additional logs on this script
    print(formatted_time[:-3] + " - " + txt)
    return 0

#find info from /tmp/es_state.inf 
def getInfoFromESState(statefile, info):
    ini = keyValueSettings(statefile, False)
    ini.loadFile(True)
    info_value = ini.getString(info, "Unknown")
    del ini
    if info_value != '':
        Log('Info found, the ' + info + ' value is ' + info_value)
    else:
        Log('No ' + info + ' found !')
    return info_value

def fetch_url(url, params):
    """Fetches a URL with query parameters using urllib.request."""

    # Encode the parameters into a query string
    query_string = urllib.parse.urlencode(params)
    url = f"{url}?{query_string}"

    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error fetching URL: {e}")
        return None

def buttons_light(system):
  # api-endpoint (using of dedicated ESP8266 (D0 to D8 on Wemos D1 Mini)
  # URL to create as: http://192.168.0.XXX/?D0=on&D1=on&D2=on&D3=on&D4=on&D5=on&D6=on&D7=on
  URL = URL_ESP8266_2
  PARAMS = {}
  # 
  for x in range(0, 8):
    if system in SYSTEMS_BUTTONS_MAPPING:
    # defining a params dict for the parameters to be sent to the API 
      if SYSTEMS_BUTTONS_MAPPING[system][x] == 1:
        state = 'on'
      else:
        state = 'off'
      PARAMS['D'+ str(x)] = state
    else:  
      # defining a params dict for the parameters to be sent to the API 
      state = 'on'
    PARAMS['D'+ str(x)] = state
  #display PARAMS  
  Log('Parameters : ' + json.dumps(PARAMS))
  # sending get request and saving the response as response object 
  r= fetch_url(url = URL, params = PARAMS)
  #extracting response text  
  Log('Result : ' + r)

def players_light(nbplayers,off=False):
  # api-endpoint (using of dedicated ESP8266 (D1 to D4 on Wemos D1 Mini))
  # URL to create as: http://192.168.0.XXX/?D1=on&D2=on&D3=on&D4
  URL = URL_ESP8266_1
  PARAMS = {}
  if off == False:
    for x in range(1, 5):
      if nbplayers >= x:
        state = 'on'
      else:
        state = 'off'
      # defining a params dict for the parameters to be sent to the API 
      PARAMS['D'+ str(x)] = state
    #display PARAMS  
    Log('Parameters : ' + json.dumps(PARAMS)) 
    # sending get request and saving the response as response object 
    r= fetch_url(url = URL, params = PARAMS)
    #extracting response text  
    Log('Result : ' + r)
  else:
    for x in range(1, 5):
      # defining a params dict for the parameters to be sent to the API 
      PARAMS['D'+ str(x)] = 'off'
    #display PARAMS  
    Log('Parameters : ' + json.dumps(PARAMS)) 
    # sending get request and saving the response as response object 
    r= fetch_url(url = URL, params = PARAMS)
    #extracting response text  
    Log('Result : ' + r)

#---------------------------------------------------------------------------------------------------
def get_args():
  parser = argparse.ArgumentParser(description='Pilotage lumieres boutons PANEL ARCADE 4 joueurs',epilog='(C) BOZO THE GEEK')
  #example of command run by pegasus asd user scripts: /usr/bin/python /recalbox/share/userscripts/PanelLight[rungame].py -action rungame -statefile /tmp/es_state.inf -param "/recalbox/share/roms/nes/micro mages.nes"
  parser.add_argument("-action", help="type of action", type=str, required=False)
  parser.add_argument("-statefile", help="state file path", type=str, required=False)
  parser.add_argument("-param", help="parameter depending of action", type=str, required=False)
  #example of command: python PanelLights.py -system mame -rom /recalbox/share/roms/mame/outrun.zip
  #example of command: python PanelLights.py -system snes -rom "/recalbox/share/roms/snes/Aladdin (France).zip"
  #example of command: python PanelLights.py -off true
  #example of command: python PanelLights.py -system atari2600 -rom "/recalbox/share/roms/atari2600/Arcade Pong (Flashback 2 Version).a26"
  parser.add_argument("-off", action='store_true', help="to poweroff the panel", required=False)
  parser.add_argument("-on", action='store_true', help="to power on the panel", required=False)
  #parser.add_argument("-p1index", help="player1 controller index", type=int, required=False)
  #parser.add_argument("-p1guid", help="player1 controller SDL2 guid", type=str, required=False)
  #parser.add_argument("-p1name", help="player1 controller name", type=str, required=False)
  #parser.add_argument("-p1devicepath", help="player1 controller device", type=str, required=False)
  #parser.add_argument("-p1nbaxes", help="player1 controller number of axes", type=str, required=False)
  #parser.add_argument("-p2index", help="player2 controller index", type=int, required=False)
  #parser.add_argument("-p2guid", help="player2 controller SDL2 guid", type=str, required=False)
  #parser.add_argument("-p2name", help="player2 controller name", type=str, required=False)
  #parser.add_argument("-p2devicepath", help="player2 controller device", type=str, required=False)
  #parser.add_argument("-p2nbaxes", help="player2 controller number of axes", type=str, required=False)
  #parser.add_argument("-p3index", help="player3 controller index", type=int, required=False)
  #parser.add_argument("-p3guid", help="player3 controller SDL2 guid", type=str, required=False)
  #parser.add_argument("-p3name", help="player3 controller name", type=str, required=False)
  #parser.add_argument("-p3devicepath", help="player3 controller device", type=str, required=False)
  #parser.add_argument("-p3nbaxes", help="player3 controller number of axes", type=str, required=False)
  #parser.add_argument("-p4index", help="player4 controller index", type=int, required=False)
  #parser.add_argument("-p4guid", help="player4 controller SDL2 guid", type=str, required=False)
  #parser.add_argument("-p4name", help="player4 controller name", type=str, required=False)
  #parser.add_argument("-p4devicepath", help="player4 controller device", type=str, required=False)
  #parser.add_argument("-p4nbaxes", help="player4 controller number of axes", type=str, required=False)
  #parser.add_argument("-p5index", help="player5 controller index", type=int, required=False)
  #parser.add_argument("-p5guid", help="player5 controller SDL2 guid", type=str, required=False)
  #parser.add_argument("-p5name", help="player5 controller name", type=str, required=False)
  #parser.add_argument("-p5devicepath", help="player5 controller device", type=str, required=False)
  #parser.add_argument("-p5nbaxes", help="player5 controller number of axes", type=str, required=False)
  parser.add_argument("-system", help="select the system to launch", type=str, required=False)
  parser.add_argument("-rom", help="rom absolute path", type=str, required=False)
  parser.add_argument("-emulator", help="force emulator", type=str, required=False)
  parser.add_argument("-core", help="force emulator core", type=str, required=False)
  parser.add_argument("-ratio", help="force game ratio", type=str, required=False)
  parser.add_argument("-demo", help="mode demo", type=bool, required=False)
  #parser.add_argument("-demoduration", help="mode demo duration in second", type=int, required=False)
  #parser.add_argument("-demoinfoduration", help="mode demo outscreen duration in second", type=int, required=False)
  #parser.add_argument("-netplay", help="host/client", type=str, required=False)
  #parser.add_argument("-netplay_ip", help="host IP", type=str, required=False)
  #parser.add_argument("-netplay_port", help="host port (not used in client mode)", type=str, required=False)
  #parser.add_argument("-hash", help="force rom crc", type=str, required=False)
  #parser.add_argument("-extra", help="pass extra argument", type=str, required=False)
  return parser.parse_args()
#------------------------------------------------------------------------------
#---------------------------------------- MAIN --------------------------------                      
#------------------------------------------------------------------------------

def main():
  #Test Arg
  args=get_args()
  
  if args.off or (args.action == "shutdown") or (args.action == "reboot"):
    #to power off all lights
    players_light(nbplayers = 4,off = True)
    sys.exit(0)  
  
  if args.on:
    #to power on all lights
    players_light(nbplayers = 4,off = False)
    buttons_light('n64')
    sys.exit(0)
  #init variables
  System = ""
  FullRomLocation = ""
  if args.action == "rungame":
    Log("args.action == rungame")
    if args.statefile != '':
      #TODO: to get system from state file
      System = getInfoFromESState(args.statefile, "SystemId")
    if args.param != '':
      Log("args.param : " + args.param)
      FullRomLocation = args.param


  else:
    if (args.system is None) or (args.rom is None) :
      print('For more information type -h as parameter')
      sys.exit(0)
    System = args.system
    FullRomLocation = args.rom
  
  Log('System parameter :' + System)
  Log('Rom parameter :' + FullRomLocation)
  
  #Lecture Configuration
  #config.load_from_file()
  
  #Execution des patchs
  #gameListPatch = GameListPatcher(config,'console',args.mode)
  #gameListPatch.start()
  #gameListPatch.join()
  
  #Chargement XML avec MiniDom :-<
  #test 1 OK
  #System = 'mame'
  #FullRomLocation = '/recalbox/share/roms/mame/outrun.zip'
  #test 2 OK
  #System = 'n64'
  #FullRomLocation = '/recalbox/share/roms/n64/Legend\ of\ Zelda,\ The\ -\ Majora\'s\ Mask.z64'
  #test 3 OK
  #System = 'megadrive'
  #FullRomLocation = '/recalbox/share/roms/megadrive/Sonic\ \&\ Knuckles\ \(World\).zip'
  #test 4 OK
  #System = 'snes'
  #FullRomLocation = '/recalbox/share/roms/snes/Tiny\ Toon\ Adventures\ -\ Wild\ \&\ Wacky\ Sports\ \(Europe\)\ \(Beta\).zip'
  #test 5 OK
  #System = 'neogeo'
  #FullRomLocation = '/recalbox/share/roms/neogeo/mslug3b6.zip'    
  RomsDirectory = FullRomLocation.split(System)[0]
  Rom = FullRomLocation.split(System)[1]
  #to remove \ if necessary
  Rom = Rom.replace("\\","")
  #gamesList = GamesList()
  #try:
  #gamesList.import_xml_file(RomsDirectory + System + os.sep + NOM_GAMELIST_XML,True)
  #Log('Gamelist file imported:' + RomsDirectory + System + os.sep + NOM_GAMELIST_XML)
  Log('Rom to find : ' + Rom)
  #game = gamesList.search_game_by_path ('.' + Rom)
  
  # if game.name != '':
    # Log('file found, the game name is :' + game.name)
  
  # if game.players != '':
    # Log('the number of player is : ' + game.players)
    # nbplayers = int(game.players[-1])
  # else:
  
  nbplayers = 4
  Log('the max number of player is : ' + str(nbplayers))
  
  players_light(nbplayers)
      
  buttons_light(System)
  
  sys.exit(0)

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
  main()
