def check_ph_ec_usecase():
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(4, GPIO.IN)
    value = GPIO.input(4)
