import RPi.GPIO as GPIO  # Import GPIO library
import time  # Import time library
import aiohttp  # Import aiohttp library
import asyncio  # Import asyncio library
from aiohttp import web  # Import web server functionalities


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


async def handle_off_request(request):
    """Handler function to turn off the balls."""
    await make_request(url_ball_1, ball_stop)
    await make_request(url_ball_2, ball_stop)
    return web.Response(text="Balls turned off")


async def start_web_server():
    """Starts the web server."""
    app = web.Application()
    app.router.add_get('/off', handle_off_request)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("HTTP Server started on http://0.0.0.0:8080")


async def measure_pulse():
    """Measure the pulse width in a non-blocking manner."""
    GPIO.output(TRIG, False)
    await asyncio.sleep(2)

    GPIO.output(TRIG, True)
    await asyncio.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = pulse_end = None

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    return pulse_start, pulse_end


####################
# # This is the blocking version of the code
# while True:

#     GPIO.output(TRIG, False)  # Set TRIG as LOW
#     print("Waiting For Sensor To Settle")
#     time.sleep(2)  # Delay of 2 seconds

#     GPIO.output(TRIG, True)  # Set TRIG as HIGH
#     time.sleep(0.00001)  # Delay of 0.00001 seconds
#     GPIO.output(TRIG, False)  # Set TRIG as LOW

#     while GPIO.input(ECHO) == 0:  # Check if Echo is LOW
#         pulse_start = time.time()  # Time of the last  LOW pulse

#     while GPIO.input(ECHO) == 1:  # Check whether Echo is HIGH
#         pulse_end = time.time()  # Time of the last HIGH pulse

#     pulse_duration = pulse_end - pulse_start  # pulse duration to a variable

#     distance = pulse_duration * 17150  # Calculate distance
#     distance = round(distance, 2)  # Round to two decimal points

#     if distance > 20 and distance < 400:  # Is distance within range
#         # Distance with calibration
#         print(f'Distance:, {distance} - 0.5, "cm"')
#         # request balls to move
#         # Send the HTTP request
#         asyncio.run(make_request(url_ball_1, ball_go))
#         asyncio.run(make_request(url_ball_2, ball_go))

#         out_of_range_time = None  # Reset the out of range time

#     else:
#         print("Out Of Range")  # display out of range
#         if out_of_range_time is None:
#             out_of_range_time = time.time()  # Record the time when it went out of range
#         elif time.time() - out_of_range_time >= passed_time:  # Check if 10 minutes have passed
#             # Send the HTTP request to balls to stop
#             asyncio.run(make_request(url_ball_1, ball_stop))
#             asyncio.run(make_request(url_ball_2, ball_stop))

#             out_of_range_time = time.time()  # Reset the out of range time

####################
# # This is async version of the code

# async def measure_distance():
#     while True:
#         GPIO.output(TRIG, False)
#         print("Waiting For Sensor To Settle")
#         await asyncio.sleep(2)

#         GPIO.output(TRIG, True)
#         await asyncio.sleep(0.00001)
#         GPIO.output(TRIG, False)

#         pulse_start = None
#         pulse_end = None

#         # This part needs to be adapted to be non-blocking
#         # For demonstration, let's assume it's handled appropriately
#         while GPIO.input(ECHO) == 0:
#             pulse_start = time.time()

#         while GPIO.input(ECHO) == 1:
#             pulse_end = time.time()

#         if pulse_start is not None and pulse_end is not None:
#             pulse_duration = pulse_end - pulse_start
#             distance = pulse_duration * 17150
#             distance = round(distance, 2)

#             if 20 < distance < 400:
#                 print(f'Distance: {distance} - 0.5 cm')
#                 await make_request(url_ball_1, ball_go)
#                 await make_request(url_ball_2, ball_go)
#                 out_of_range_time = None
#             else:
#                 print("Out Of Range")
#                 if out_of_range_time is None:
#                     out_of_range_time = time.time()
#                 elif time.time() - out_of_range_time >= passed_time:
#                     await make_request(url_ball_1, ball_stop)
#                     await make_request(url_ball_2, ball_stop)
#                     out_of_range_time = time.time()

####################
# # This is the async version of the code with the blocking part separated

async def measure_distance():
    while True:
        pulse_start, pulse_end = await asyncio.to_thread(measure_pulse)

        if pulse_start is not None and pulse_end is not None:
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance, 2)

            if 20 < distance < 400:
                print(f'Distance: {distance} - 0.5 cm')
                await make_request(url_ball_1, ball_go)
                await make_request(url_ball_2, ball_go)
            else:
                print("Out Of Range")


async def main():
    await asyncio.gather(
        start_web_server(),
        measure_distance()
    )

if __name__ == "__main__":
    asyncio.run(main())
