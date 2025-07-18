import time

class PID:
    def __init__(self, Kp, Ki, Kd, setpoint, sample_time=1, output_limits=(0, 1023)):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.sample_time = sample_time
        self.output_limits = output_limits

        self._last_time = time.ticks_ms()
        self._last_input = 0
        self._proportional = 0
        self._integral = 0
        self._derivative = 0
        self.output = 0

    def update(self, input_):
        now = time.ticks_ms()
        time_change = time.ticks_diff(now, self._last_time)

        if time_change >= self.sample_time * 1000:
            error = self.setpoint - input_
            
            # Proportional term
            self._proportional = self.Kp * error

            # Integral term
            self._integral += self.Ki * error * (time_change / 1000)
            self._integral = max(min(self._integral, self.output_limits[1]), self.output_limits[0])

            # Derivative term
            d_input = input_ - self._last_input
            self._derivative = self.Kd * (-d_input / (time_change / 1000))

            # Compute PID output
            self.output = self._proportional + self._integral + self._derivative
            self.output = max(min(self.output, self.output_limits[1]), self.output_limits[0])

            self._last_input = input_
            self._last_time = now

        return self.output

    def set_tunings(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
