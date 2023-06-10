# DOCS: https://docs.micropython.org/en/latest/rp2/quickref.html
import gc
import machine
from machine import Pin, Timer
from phew import server, logging, access_point, dns
from phew.server import redirect
from phew.template import render_template
gc.threshold(50000) # configure garbage collection

DOMAIN = "pico-w"
WLAN_NAME = DOMAIN
WLAN_PWD = None

LED = Pin("LED", Pin.OUT)

# LED_TIMER = Timer(-1) # -1 = virtual timer? SEE https://docs.micropython.org/en/latest/library/machine.html#machine-callbacks
# def led_blink(on_millis = 100):
#     # blink the LED for the given number of milliseconds
#     LED.toggle()
#     LED_TIMER.init(mode=Timer.ONE_SHOT, period=0.2, callback=LED.toggle)

@server.route("/", methods=["GET","POST"])
def http_index(request):
    LED.toggle()
    if request.method == "GET":
        logging.debug("Get request")
        return """
<h1>Not implemented yet</h1>
<br>
<br>
<a href="/softreset">Restart</a>
"""
    if request.method == "POST":
        data = request.form.get("data", None)
        logging.debug("Parameter 'data':", data)
        return render_template("index.html", data=data)
    


# Functions for resets (no more unplugging to update the programming)
@server.route("/reset")
def http_bootloader(request):
    logging.warn("Hard reset")
    machine.reset()

@server.route("/softreset")
def http_bootloader(request):
    logging.warn("Soft reset")
    machine.soft_reset()

@server.route("/bootloader")
def http_bootloader(request):
    logging.warn("Hard reset and opening bootloader")
    machine.bootloader()


# Redirect to application
@server.catchall()
def http_catch_all(request):
    LED.toggle()
    logging.debug("Catchall")
    logging.debug("  Host:", request.headers.get("host"))
    logging.debug("  Path:", request.uri)
    return redirect("http://" + DOMAIN + "/")


ap = access_point(WLAN_NAME, WLAN_PWD)
logging.info(f"Started access point '{WLAN_NAME}' with password '{WLAN_PWD}'")
ip = ap.ifconfig()[0]
# Redirect all DNS requests to me
dns.run_catchall(ip)
# Tell console we are running
logging.info(f"Server running at '{DOMAIN}' ({ip})")

# show that we are running and have not seen any requests yet
LED.on()
# run the web server. The method does not return
server.run()

