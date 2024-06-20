import RPi.GPIO as GPIO  # Import GPIO library
import time  # Import time library
import aiohttp  # Import aiohttp library
import asyncio  # Import asyncio library

GPIO.setmode(GPIO.BCM)  # Set GPIO pin numbering

TRIG = 15  # Associate pin 15 to TRIG
ECHO = 14  # Associate pin 14 to Echo

print("Distance measurement in progress")

GPIO.setup(TRIG, GPIO.OUT)  # Set pin as GPIO out
GPIO.setup(ECHO, GPIO.IN)  # Set pin as GPIO in


out_of_range_time = None
passed_time = 600  # 10 minutes

url_ball_1 = "http://192.168.1.11"
url_ball_2 = "http://192.168.1.12"

ball_go = "on"
ball_stop = "off"


async def make_request(url, state):
    request_url = f"{url}/{state}"
    async with aiohttp.ClientSession() as session:
        async with session.get(request_url) as resp:
            print(f"{request_url} Response: {resp.status}")

while True:

    GPIO.output(TRIG, False)  # Set TRIG as LOW
    print("Waiting For Sensor To Settle")
    time.sleep(2)  # Delay of 2 seconds

    GPIO.output(TRIG, True)  # Set TRIG as HIGH
    time.sleep(0.00001)  # Delay of 0.00001 seconds
    GPIO.output(TRIG, False)  # Set TRIG as LOW

    while GPIO.input(ECHO) == 0:  # Check if Echo is LOW
        pulse_start = time.time()  # Time of the last  LOW pulse

    while GPIO.input(ECHO) == 1:  # Check whether Echo is HIGH
        pulse_end = time.time()  # Time of the last HIGH pulse

    pulse_duration = pulse_end - pulse_start  # pulse duration to a variable

    distance = pulse_duration * 17150  # Calculate distance
    distance = round(distance, 2)  # Round to two decimal points

    if distance > 20 and distance < 400:  # Is distance within range
        # Distance with calibration
        print(f'Distance:, {distance} - 0.5, "cm"')
        # request balls to move
        # Send the HTTP request
        asyncio.run(make_request(url_ball_1, ball_go))
        asyncio.run(make_request(url_ball_2, ball_go))

        out_of_range_time = None  # Reset the out of range time

    else:
        print("Out Of Range")  # display out of range
        if out_of_range_time is None:
            out_of_range_time = time.time()  # Record the time when it went out of range
        elif time.time() - out_of_range_time >= passed_time:  # Check if 10 minutes have passed
            # Send the HTTP request to balls to stop
            asyncio.run(make_request(url_ball_1, ball_stop))
            asyncio.run(make_request(url_ball_2, ball_stop))

            out_of_range_time = time.time()  # Reset the out of range time
