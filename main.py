import network
import socket
import machine
import time
import ujson


ssid = "Pixel 9 Pro"
password = "Arty7059"

# Temperature sensor
sensor = machine.ADC(4)
conversion = 3.3 / 65535

def read_temp():
    reading = sensor.read_u16() * conversion
    temp = 27 - (reading - 0.706)/0.001721
    return round(temp,2)

# WiFi connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    time.sleep(1)

print("Connected:", wlan.ifconfig())

# Data storage
data = []

# Web page
def html_page():
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<title>Pico Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>

</head>
<body class="flex justify-center items-center h-screen bg-slate-950">


<div
  class="group relative flex
 w-80 flex-col rounded-xl bg-slate-950 p-4 shadow-2xl transition-all duration-300 hover:scale-[1.02] hover:shadow-indigo-500/20"
>
  <div
    class="absolute inset-0 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-20 blur-sm transition-opacity duration-300 group-hover:opacity-30"
  ></div>
  <div class="absolute inset-px rounded-[11px] bg-slate-950"></div>

  <div class="relative">
    <div class="mb-4 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500">
        
     <img width="48" height="48" src="https://img.icons8.com/color/48/raspberry-pi.png" alt="raspberry-pi"/> 
          
        </div>
        <h3 class="text-sm font-semibold text-white">Pico Dashboard</h3>
      </div>

      <span
        class="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-1 text-xs font-medium text-emerald-500"
      >
        <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
        Conected
      </span>
    </div>

    <div class="mb-4 grid gap-4">
      

      <div class="rounded-lg bg-slate-900/50 p-3">
        <p class="text-xs font-medium text-slate-400">Current Temperature</p>
        <p class="text-lg font-semibold text-white" id="current-temp">-- C</p>
        <span class="text-xs font-medium text-emerald-500">Healty: Good :)</span>
      </div>
    </div>

    <div
      class="mb-4 h-40 w-full overflow-hidden rounded-lg bg-slate-900/50 p-3"
    >
      <div class="flex h-full w-full items-end justify-between gap-1">
        
         
       
       
         <canvas id="chart"></canvas>
      
         
     
      
       
     </div>
    </div>

    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-xs font-medium text-slate-400">Created By Eydenco</span>
        
      </div>
    </div>
  </div>
</div>


<!-- JS -->
<script>
let ctx = document.getElementById('chart');
let chart = new Chart(ctx,{
type:'line',
data:{labels:[],datasets:[{label:'Temp C',data:[]} ]},
options:{animation:false,responsive:true,maintainAspectRatio:false}
});

async function update(){
  let r = await fetch('/data?t=' + Date.now());
  let d = await r.json();
  
  // Update chart
  chart.data.labels = Array(d.length).fill('');
  chart.data.datasets[0].data = d;
  chart.update();
  
  // Update current temperature block
  if(d.length>0){
    document.getElementById('current-temp').innerText = d[d.length-1] + " C";
  }
  
}

setInterval(update,2000);
</script>


</body>
</html>
"""



# Server
addr = socket.getaddrinfo('0.0.0.0',80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(5)

print("Server running...")

while True:
    try:
        client, addr = server.accept()
        request = client.recv(1024)
        request = str(request)

        # Read sensor
        temp = read_temp()
        data.append(temp)
        if len(data) > 20:
            data.pop(0)

        # Serve JSON data for chart
        if '/data' in request:
            client.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            client.send(ujson.dumps(data))
        else:
            client.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            client.send(html_page())

        client.close()

    except Exception as e:
        print("Error:", e)




